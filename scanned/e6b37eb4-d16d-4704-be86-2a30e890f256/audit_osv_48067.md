# [H] CVE-2017-17805

## Summary
Severity: High
Advisory: CVE-2017-17805
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17805
Type: osv

## Details
The Salsa20 encryption algorithm in the Linux kernel before 4.14.8 does not correctly handle zero-length inputs, allowing a local attacker able to use the AF_ALG-based skcipher interface (CONFIG_CRYPTO_USER_API_SKCIPHER) to cause a denial of service (uninitialized-memory free and kernel crash) or have unspecified other impact by executing a crafted sequence of system calls that use the blkcipher_walk API. Both the generic implementation (crypto/salsa20_generic.c) and x86 implementation (arch/x86/crypto/salsa20_glue.c) of Salsa20 were vulnerable.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00004.html
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3620-1/
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00008.html
- https://access.redhat.com/errata/RHSA-2018:2948
- https://usn.ubuntu.com/3632-1/
- https://www.debian.org/security/2017/dsa-4073
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00016.html
- https://access.redhat.com/errata/RHSA-2018:3096
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3620-2/
- https://www.debian.org/security/2018/dsa-4082
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://www.securityfocus.com/bid/102291
- https://access.redhat.com/errata/RHSA-2018:3083
