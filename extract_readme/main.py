import re
import html
import requests
import mimetypes
import pyperclip
from github import Github
from bs4 import BeautifulSoup
from argparse import ArgumentParser

import mistletoe
from mistletoe import span_token, block_token, Document
from mistletoe.html_renderer import HTMLRenderer

raw_data_root = "https://raw.githubusercontent.com"

def get_readme_content(user_name, repo_name):
    g = Github()

    try:
        repo = g.get_repo(f"{user_name}/{repo_name}")
    except Exception as e:
        print(f"Repository \"{user_name}/{repo_name}\" not found!")
        exit()
    
    contents = repo.get_contents("")
    readme_content = None
    for content in contents:
        if re.match("(?i)readme*", content.path) is not None:
            readme_content = requests.get(content.download_url).text # readme raw content
    if readme_content is None:
        print(f"Repository \"{user_name}/{repo_name}\" does not have a readme file!")
        exit()
    
    return readme_content

def get_new_src(src, user, repo, raw_data_root):
    if src.startswith("http"):
        return src
    new_src = src.lstrip("./")
    new_src = "/".join([raw_data_root, user, repo, "master", new_src])
    return new_src

def process_html(token, user, repo, raw_data_root):
    soup = BeautifulSoup(token.content, "html.parser")
    img_tags = soup.find_all("img")
    for i in range(len(img_tags)):
        src = img_tags[i]["src"]
        img_tags[i]["src"] = get_new_src(src, user, repo, raw_data_root)
        if img_tags[i]["width"] is None:
            img_tags[i]["width"] = "50%"
        p = soup.new_tag("p", align="center")
        img_tags[i].wrap(p)
    return soup.prettify()

class READMERenderer(HTMLRenderer):
    def __init__(self, user, repo, *args, **kwargs):
        super(READMERenderer, self).__init__(*args, **kwargs)
        self.user = user
        self.repo = repo
    
    def render(self, token):
        try:
            for i in range(len(token.children)):
                token.children[i].parent = token
        except:
            pass
        return self.render_map[token.__class__.__name__](token)

    def render_inner(self, token) -> str:
        for i in range(len(token.children)):
            token.children[i].parent = token
        try:
            for i in range(len(token.header)):
                token.header[i].parent = token
        except:
            pass
        return ''.join(map(self.render, token.children))

    def render_html_span(self, token: span_token.HTMLSpan) -> str:
        return process_html(token, self.user, self.repo, raw_data_root)

    def render_html_block(self, token: block_token.HTMLBlock) -> str:
        return process_html(token, self.user, self.repo, raw_data_root)

    def render_table_row(self, token: block_token.TableRow, is_header=False) -> str:
        template = '<tr>\n{inner}</tr>\n'
        inner = ''.join([self.render_table_cell(child, is_header)
                         for child in token.children])
        return template.format(inner=inner)

    def render_table_cell(self, token: block_token.TableCell, is_header=False) -> str:
        width = 100 / len(token.parent.children)
        
        template = '<{tag}{attr} style="width:{width}%;">{inner}</{tag}>\n'
        tag = 'th' if is_header else 'td'
        if token.align is None:
            align = 'left'
        elif token.align == 0:
            align = 'center'
        elif token.align == 1:
            align = 'right'
        attr = ' align="{}"'.format(align)
        inner = self.render_inner(token)
        return template.format(tag=tag, width=width, attr=attr, inner=inner)

    def render_table(self, token: block_token.Table) -> str:
        template = '<p><br></p><table style="width:100%;margin:auto">\n{inner}</table><p><br></p>'
        if hasattr(token, 'header'):
            token.header.parent = token
            for i in range(len(token.header.children)):
                token.header.children[i].parent = token.header
            head_template = '<thead>\n{inner}</thead>\n'
            head_inner = self.render_table_row(token.header, is_header=True)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        body_template = '<tbody>\n{inner}</tbody>\n'
        body_inner = self.render_inner(token)
        body_rendered = body_template.format(inner=body_inner)
        return template.format(inner=head_rendered+body_rendered)

    def render_image(self, token: span_token.Image) -> str:
        if isinstance(token.parent, block_token.TableCell):
            width = "100%"
        else:
            width = "50%"
        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        new_src = get_new_src(token.src, self.user, self.repo, raw_data_root)
        
        media_type = mimetypes.guess_type(new_src)[0]
        if media_type.startswith("video"):
            template = '<p align="center"><video width={} controls><source src={} type={}></source></video></p>'
            return template.format(width, new_src, media_type)
        else:
            template = '<p align="center"><img src="{}" alt="{}"{} width="{}"/></p>'
            return template.format(new_src, self.render_to_plain(token), title, width)
    

def main():
    parser = ArgumentParser()
    parser.add_argument("user")
    parser.add_argument("repo")
    args = parser.parse_args()

    user = args.user
    repo = args.repo

    readme_content = get_readme_content(user, repo)
    with READMERenderer(user, repo) as renderer:
        markdown = renderer.render(Document(readme_content))
    pyperclip.copy(markdown)
