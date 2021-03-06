# extract-readme
`extract-readme` extracts the README markdown file from a GitHub repository and generates a corresponding formatted HTML that can be rendered on any website.

## What for?
Sometimes you may want to mirror a README file of your project on your personal website. However, you might encounter serveral problems:

1. Your website does not support vanilla markdown.
2. File paths in the README file are relative to the repository folder structure, and cannot be accessed from outside of the repository.
3. Image and table sizes are not dynamically adjusted to fit the website frame.
4. ...

This script takes care of these issues.
## Features
- Parses, formats, and renders ...
	- Images, video content
    - Tables
    - HTML embedded in markdown
- Peforms regex matching for readme files (`README`, `readme.md`, `ReAdMe.md`, etc)
- Dynamic scaling of image, video, and table content

## Usage
Install the package:
```cmd
git clone https://github.com/bchao1/extract-readme.git
cd extract-readme 
python3 -m pip install .
```

Run the following command:
```cmd
extract-readme user repo
```

- `user`: the GitHub user handle
- `repo`: repository name

The formatted HTML file will be copied to your clipboard. Simply embed the copied content in your website HTML code. 

## Example
Original markdown:
```markdown
# Poisson image editing

A fast, scalable, and extensive implementation of the [Poisson Image Editing](https://dl.acm.org/doi/10.1145/882262.882269) paper by Perez et al. 2003.

![teaser](data/teaser.png)
```

Generated HTML:
```html
<h1>Poisson image editing</h1>
<p>A fast, scalable, and extensive implementation of the <a href="https://dl.acm.org/doi/10.1145/882262.882269">Poisson
        Image Editing</a> paper by Perez et al. 2003.</p>
<p>
<p align="center"><img src="https://raw.githubusercontent.com/bchao1/poisson-image-editing/master/data/teaser.png"
        alt="teaser" width="80%" /></p>
</p>
```

|Original markdown|Generated HTML|
|---|---|
|![](images/md_title.png)|![](images/html_title.png)|
|![](images/md_table.png)|![](images/html_table.png)|

Note that this script only generates a bare-bones HTML. You can either customize it later by defining your own `style.css` file that complements the HTML, or the HTML with directly inherit the style of your website.

## Todo
- Additional size logic for `svg/xml` files. 