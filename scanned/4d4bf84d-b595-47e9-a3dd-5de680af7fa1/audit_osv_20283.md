# [H] CVE-2021-32706

## Summary
Severity: High
Advisory: CVE-2021-32706
Aliases: GHSA-5cm9-6p3m-v259
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2021-32706
Type: osv

## Details
Pi-hole's Web interface provides a central location to manage a Pi-hole instance and review performance statistics. Prior to Pi-hole Web interface version 5.5.1, the `validDomainWildcard` preg_match filter allows a malicious character through that can be used to execute code, list directories, and overwrite sensitive files. The issue lies in the fact that one of the periods is not escaped, allowing any character to be used in its place. A patch for this vulnerability was released in version 5.5.1.

## References
- https://github.com/pi-hole/AdminLTE/releases/tag/v5.5.1
- https://github.com/pi-hole/AdminLTE/security/advisories/GHSA-5cm9-6p3m-v259
