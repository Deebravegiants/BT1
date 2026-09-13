# [M] CVE-2018-12435

## Summary
Severity: Medium
Advisory: CVE-2018-12435
CVSS: 5.9 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12435
Type: osv

## Details
Botan 2.5.0 through 2.6.0 before 2.7.0 allows a memory-cache side-channel attack on ECDSA signatures, aka the Return Of the Hidden Number Problem or ROHNP, related to dsa/dsa.cpp, ec_group/ec_group.cpp, and ecdsa/ecdsa.cpp. To discover an ECDSA key, the attacker needs access to either the local machine or a different virtual machine on the same physical host.

## References
- https://botan.randombit.net/security.html
- https://github.com/randombit/botan/commit/48fc8df51d99f9d8ba251219367b3d629cc848e3
- https://www.nccgroup.trust/us/our-research/technical-advisory-return-of-the-hidden-number-problem/
