# [H] CVE-2014-3856

## Summary
Severity: High
Advisory: CVE-2014-3856
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2014-3856
Type: osv

## Details
The funced function in fish (aka fish-shell) 1.23.0 before 2.1.1 does not properly create temporary files, which allows local users to gain privileges via a temporary file with a predictable name.

## References
- https://github.com/fish-shell/fish-shell/issues/1437
- https://github.com/fish-shell/fish-shell/releases/tag/2.1.1
- https://www.openwall.com/lists/oss-security/2014/04/28/4
- https://www.openwall.com/lists/oss-security/2014/04/28/4
