# [M] CVE-2018-12437

## Summary
Severity: Medium
Advisory: CVE-2018-12437
CVSS: 4.9 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12437
Type: osv

## Details
LibTomCrypt through 1.18.1 allows a memory-cache side-channel attack on ECDSA signatures, aka the Return Of the Hidden Number Problem or ROHNP. To discover an ECDSA key, the attacker needs access to either the local machine or a different virtual machine on the same physical host.

## References
- https://security.gentoo.org/glsa/202007-53
- https://www.nccgroup.trust/us/our-research/technical-advisory-return-of-the-hidden-number-problem/
