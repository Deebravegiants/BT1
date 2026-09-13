# [M] CVE-2021-28690

## Summary
Severity: Medium
Advisory: CVE-2021-28690
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-29
Source: https://osv.dev/vulnerability/CVE-2021-28690
Type: osv

## Details
x86: TSX Async Abort protections not restored after S3 This issue relates to the TSX Async Abort speculative security vulnerability. Please see https://xenbits.xen.org/xsa/advisory-305.html for details. Mitigating TAA by disabling TSX (the default and preferred option) requires selecting a non-default setting in MSR_TSX_CTRL. This setting isn't restored after S3 suspend.

## References
- https://security.gentoo.org/glsa/202107-30
- https://xenbits.xenproject.org/xsa/advisory-377.txt
