# [M] CVE-2022-27672

## Summary
Severity: Medium
Advisory: CVE-2022-27672
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/CVE-2022-27672
Type: osv

## Details
When SMT is enabled, certain AMD processors may speculatively execute instructions using a target
from the sibling thread after an SMT mode switch potentially resulting in information disclosure.

## References
- https://security.gentoo.org/glsa/202402-07
- https://www.amd.com/en/corporate/product-security/bulletin/AMD-SB-1045
- http://xenbits.xen.org/xsa/advisory-426.html
- https://www.amd.com/en/corporate/product-security/bulletin/AMD-SB-1045
