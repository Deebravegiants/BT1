# [H] CVE-2017-18075

## Summary
Severity: High
Advisory: CVE-2017-18075
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2017-18075
Type: osv

## Details
crypto/pcrypt.c in the Linux kernel before 4.14.13 mishandles freeing instances, allowing a local user able to access the AF_ALG-based AEAD interface (CONFIG_CRYPTO_USER_API_AEAD) and pcrypt (CONFIG_CRYPTO_PCRYPT) to cause a denial of service (kfree of an incorrect pointer) or possibly have unspecified other impact by executing a crafted sequence of system calls.

## References
- http://www.securityfocus.com/bid/102813
- https://access.redhat.com/errata/RHSA-2018:2948
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.13
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d76c68109f37cb85b243a1cf0f40313afd2bae68
- https://github.com/torvalds/linux/commit/d76c68109f37cb85b243a1cf0f40313afd2bae68
