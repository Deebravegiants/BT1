# [H] CVE-2016-10037

## Summary
Severity: High
Advisory: CVE-2016-10037
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-12-24
Source: https://osv.dev/vulnerability/CVE-2016-10037
Type: osv

## Details
Directory traversal in /connectors/index.php in MODX Revolution before 2.5.2-pl allows remote attackers to perform local file inclusion/traversal/manipulation via a crafted id (aka dir) parameter, related to browser/directory/getlist.

## References
- http://www.securityfocus.com/bid/95127
- https://raw.githubusercontent.com/modxcms/revolution/v2.5.2-pl/core/docs/changelog.txt
- https://github.com/modxcms/revolution/pull/13177
