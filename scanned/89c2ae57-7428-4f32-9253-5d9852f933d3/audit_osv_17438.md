# [M] CVE-2020-15171

## Summary
Severity: Medium
Advisory: CVE-2020-15171
Aliases: GHSA-7qw5-pqhc-xm4g
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-10
Source: https://osv.dev/vulnerability/CVE-2020-15171
Type: osv

## Details
In XWiki before versions 11.10.5 or 12.2.1, any user with SCRIPT right (EDIT right before XWiki 7.4) can gain access to the application server Servlet context which contains tools allowing to instantiate arbitrary Java objects and invoke methods that may lead to arbitrary code execution. The only workaround is to give SCRIPT right only to trusted users.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-7qw5-pqhc-xm4g
