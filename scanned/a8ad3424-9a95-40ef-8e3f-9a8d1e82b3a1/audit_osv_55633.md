# [M] CVE-2026-23903

## Summary
Severity: Medium
Advisory: CVE-2026-23903
Aliases: GHSA-c244-p6m5-vqj6
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-23903
Type: osv

## Details
Authentication Bypass by Alternate Name vulnerability in Apache Shiro.

This issue affects Apache Shiro: before 2.0.7.

Users are recommended to upgrade to version 2.0.7, which fixes the issue.

The issue only effects static files. If static files are served from a case-insensitive filesystem,
such as default macOS setup, static files may be accessed by varying the case of the filename in the request.
If only lower-case (common default) filters are present in Shiro, they may be bypassed this way.

Shiro 2.0.7 and later has a new parameters to remediate this issue
shiro.ini: filterChainResolver.caseInsensitive = true
application.propertie: shiro.caseInsensitive=true

Shiro 3.0.0 and later (upcoming) makes this the default.

## References
- https://lists.apache.org/thread/5jjf0hnjcol58z2m5y255c7scz1lnp8k
- http://www.openwall.com/lists/oss-security/2026/02/08/1
