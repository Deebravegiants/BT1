# [M] CVE-2016-10318

## Summary
Severity: Medium
Advisory: CVE-2016-10318
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/CVE-2016-10318
Type: osv

## Details
A missing authorization check in the fscrypt_process_policy function in fs/crypto/policy.c in the ext4 and f2fs filesystem encryption support in the Linux kernel before 4.7.4 allows a user to assign an encryption policy to a directory owned by a different user, potentially creating a denial of service.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.4
- http://www.securityfocus.com/bid/97404
- https://github.com/torvalds/linux/commit/163ae1c6ad6299b19e22b4a35d5ab24a89791a98
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=163ae1c6ad6299b19e22b4a35d5ab24a89791a98
