# [M] CVE-2020-17049

## Summary
Severity: Medium
Advisory: CVE-2020-17049
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-11
Source: https://osv.dev/vulnerability/CVE-2020-17049
Type: osv

## Details
A security feature bypass vulnerability exists in the way Key Distribution Center (KDC) determines if a service ticket can be used for delegation via Kerberos Constrained Delegation (KCD).
To exploit the vulnerability, a compromised service that is configured to use KCD could tamper with a service ticket that is not valid for delegation to force the KDC to accept it.
The update addresses this vulnerability by changing how the KDC validates service tickets used with KCD.

## References
- http://www.openwall.com/lists/oss-security/2021/11/10/3
- https://security.gentoo.org/glsa/202309-06
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-17049
