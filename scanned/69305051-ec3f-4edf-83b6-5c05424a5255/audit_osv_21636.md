# [H] CVE-2021-44664

## Summary
Severity: High
Advisory: CVE-2021-44664
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2021-44664
Type: osv

## Details
An Authenticated Remote Code Exection (RCE) vulnerability exists in Xerte through 3.9 in website_code/php/import/fileupload.php by uploading a maliciously crafted PHP file though the project interface disguised as a language file to bypasses the upload filters. Attackers can manipulate the files destination by abusing path traversal in the 'mediapath' variable.

## References
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/1672d6f46bbd6f6d42f0903ce9a313927ae2836b#diff-27433bb0be90e431d40986f9afebe9ee2f8d1025a7f9e55c3cd7a86f1f8e3fdc
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/6daeb81d089d4a561e22f931fff1327660a7d1b5
- http://packetstormsecurity.com/files/166182/Xerte-3.9-Remote-Code-Execution.html
- https://riklutz.nl/2021/11/03/authenticated-file-upload-to-remote-code-execution-in-xerte/
