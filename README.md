# extract-readme
Extract README markdown file from GitHub repository and generate formatted HTML that can be rendered on any website.

## What for?
Sometimes you may want to mirror a README file of your project on your academic personal website. However, you might encounter serveral problems:

1. Your website does not support vanilla markdown.
2. File paths in the README file are relative to the repository folder structure, and cannot be accessed from outside of the repository.
3. Image and table sizes are not dynamically adjusted to fit the website frame.
4. ...

This script takes care of these issues.

## Usage
```
python3 extract_readme.py user repo
```

- `user`: the GitHub user handle
- `repo`: repository name

The formatted HTML file will be copied to your clipboard. Simply paste the copied content on your website HTML code.