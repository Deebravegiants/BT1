# [H] CVE-2016-9283

## Summary
Severity: High
Advisory: CVE-2016-9283
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-11-11
Source: https://osv.dev/vulnerability/CVE-2016-9283
Type: osv

## Details
SQL Injection in framework/core/subsystems/expRouter.php in Exponent CMS v2.4.0 allows remote attackers to read database information via address/addContentToSearch/id/ and a trailing string, related to a "sef URL" issue.

## References
- http://www.securitytracker.com/id/1037281
- http://www.securityfocus.com/bid/94296
- https://github.com/exponentcms/exponent-cms/commit/559792be727f4e731bfcb3935f5beec7749e9ce9
