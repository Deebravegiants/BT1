# [H] CVE-2017-17806

## Summary
Severity: High
Advisory: CVE-2017-17806
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17806
Type: osv

## Details
The HMAC implementation (crypto/hmac.c) in the Linux kernel before 4.14.8 does not validate that the underlying cryptographic hash algorithm is unkeyed, allowing a local attacker able to use the AF_ALG-based hash interface (CONFIG_CRYPTO_USER_API_HASH) and the SHA-3 hash algorithm (CONFIG_CRYPTO_SHA3) to cause a kernel stack buffer overflow by executing a crafted sequence of system calls that encounter a missing SHA-3 initialization.

## References
- https://usn.ubuntu.com/3632-1/
- https://www.debian.org/security/2017/dsa-4073
- http://www.securityfocus.com/bid/102293
- https://access.redhat.com/errata/RHSA-2018:2948
- https://usn.ubuntu.com/3617-1/
- https://lists.debian.org/debian-lts-announce/2018/01/msg00004.html
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-2/
- https://www.debian.org/security/2018/dsa-4082
- https://usn.ubuntu.com/3619-1/
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.8
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00014.html
- https://github.com/torvalds/linux/commit/af3ff8045bbf3e32f1a448542e73abb4c8ceb6f1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=af3ff8045bbf3e32f1a448542e73abb4c8ceb6f1
