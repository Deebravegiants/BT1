# [M] CVE-2018-12436

## Summary
Severity: Medium
Advisory: CVE-2018-12436
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12436
Type: osv

## Details
wolfcrypt/src/ecc.c in wolfSSL before 3.15.1.patch allows a memory-cache side-channel attack on ECDSA signatures, aka the Return Of the Hidden Number Problem or ROHNP. To discover an ECDSA key, the attacker needs access to either the local machine or a different virtual machine on the same physical host.

## References
- https://www.nccgroup.trust/us/our-research/technical-advisory-return-of-the-hidden-number-problem/
- https://www.wolfssl.com/wolfssh-and-rohnp/
- https://github.com/wolfSSL/wolfssl/commit/9b9568d500f31f964af26ba8d01e542e1f27e5ca
