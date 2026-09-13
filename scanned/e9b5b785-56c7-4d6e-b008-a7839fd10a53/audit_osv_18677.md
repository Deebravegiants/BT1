# [C] CVE-2020-35314

## Summary
Severity: Critical
Advisory: CVE-2020-35314
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-20
Source: https://osv.dev/vulnerability/CVE-2020-35314
Type: osv

## Details
A remote code execution vulnerability in the installUpdateThemePluginAction function in index.php in WonderCMS 3.1.3, allows remote attackers to upload a custom plugin which can contain arbitrary code and obtain a webshell via the theme/plugin installer.

## References
- https://github.com/robiso/wondercms
- https://packetstormsecurity.com/files/160311/WonderCMS-3.1.3-Remote-Code-Execution.html
- https://zetc0de.github.io/post/authenticated-rce-ssrf-wondercms/
- https://zetc0de.github.io/post/authenticated-rce-ssrf-wondercms/#authenticated-remote-code-execution
