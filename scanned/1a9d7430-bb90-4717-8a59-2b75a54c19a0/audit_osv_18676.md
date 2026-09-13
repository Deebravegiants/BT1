# [C] CVE-2020-35313

## Summary
Severity: Critical
Advisory: CVE-2020-35313
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-20
Source: https://osv.dev/vulnerability/CVE-2020-35313
Type: osv

## Details
A server-side request forgery (SSRF) vulnerability in the addCustomThemePluginRepository function in index.php in WonderCMS 3.1.3 allows remote attackers to execute arbitrary code via a crafted URL to the theme/plugin installer.

## References
- https://github.com/robiso/wondercms
- https://packetstormsecurity.com/files/160310/WonderCMS-3.1.3-Code-Execution-Server-Side-Request-Forgery.html
- https://zetc0de.github.io/post/authenticated-rce-ssrf-wondercms/
