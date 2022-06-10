import requests
import mistletoe
from mistletoe import span_token, block_token, Document
from mistletoe.html_renderer import HTMLRenderer
import pyperclip
from argparse import ArgumentParser
import html
from bs4 import BeautifulSoup

raw_data_root = "https://raw.githubusercontent.com"

def process_html(token, user, repo, raw_data_root):
    soup = BeautifulSoup(token.content, "html.parser")
    img_tags = soup.find_all("img")
    for i in range(len(img_tags)):
        src = img_tags[i]["src"]
        new_src = src.lstrip("./")
        new_src = "/".join([raw_data_root, user, repo, "master", new_src])
        img_tags[i]["src"] = new_src
        img_tags[i]["width"] = "100%"
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
        #print(type(token))
        #if isinstance(token, block_token.TableRow):
        #    print(token.__dict__)
        for i in range(len(token.children)):
            token.children[i].parent = token
        try:
            for i in range(len(token.header)):
                token.header[i].parent = token
        except:
            pass
            #if isinstance(token.children[i], block_token.TableRow):
            #    print(token.children[i].__dict__)
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
        if is_header:
            width = 100 / len(token.parent.children)
        else:
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
        # This is actually gross and I wonder if there's a better way to do it.
        #
        # The primary difficulty seems to be passing down alignment options to
        # reach individual cells.
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
            width = "80%"
        template = '<p align="center"><img src="{}" alt="{}"{} width="{}"/></p>'
        if token.title:
            title = ' title="{}"'.format(html.escape(token.title))
        else:
            title = ''
        new_src = token.src.lstrip("./")
        new_src = "/".join([raw_data_root, self.user, self.repo, "master", new_src])
        return template.format(new_src, self.render_to_plain(token), title, width)
    

def main():
    parser = ArgumentParser()
    parser.add_argument("user")
    parser.add_argument("repo")
    args = parser.parse_args()

    user = args.user
    repo = args.repo

    readme_url = "/".join([raw_data_root, args.user, args.repo, "master", "README.md"]) # readme or README
    readme_content = requests.get(readme_url).text # readme raw content
    with READMERenderer(user, repo) as renderer:
        markdown = renderer.render(Document(readme_content))
    pyperclip.copy(markdown)
