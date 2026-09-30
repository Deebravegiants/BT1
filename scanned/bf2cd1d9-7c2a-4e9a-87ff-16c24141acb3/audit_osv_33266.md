# [H] i40e: fix idx validation in i40e_validate_queue_map

## Summary
Severity: High
Advisory: CVE-2025-39972
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39972
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: fix idx validation in i40e_validate_queue_map

Ensure idx is within range of active/initialized TCs when iterating over
vf->ch[idx] in i40e_validate_queue_map().

## References
- https://git.kernel.org/stable/c/34dfac0c904829967d500c51f216916ce1452957
- https://git.kernel.org/stable/c/4d5e804a9e19b639b18fd13664dbad3c03c79e61
- https://git.kernel.org/stable/c/50a1e2f50f6c22b93b94eb8d168a1be3c05bf5cd
- https://git.kernel.org/stable/c/6f15a7b34fae75e745bdc2ec05e06ddfd0dd2f3c
- https://git.kernel.org/stable/c/aa68d3c3ac8d1dcec40d52ae27e39f6d32207009
- https://git.kernel.org/stable/c/b6cb93a7ff208f324c7ec581d72995f80e115e0e
- https://git.kernel.org/stable/c/cc4191e8ef40d2249c1b9a8617d22ec8a976b574
- https://git.kernel.org/stable/c/d4e3eaaa3cb3af77836d806c89cd6ebf533a7320
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39972.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39972
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
