# [H] CVE-2016-9313

## Summary
Severity: High
Advisory: CVE-2016-9313
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-9313
Type: osv

## Details
security/keys/big_key.c in the Linux kernel before 4.8.7 mishandles unsuccessful crypto registration in conjunction with successful key-type registration, which allows local users to cause a denial of service (NULL pointer dereference and panic) or possibly have unspecified other impact via a crafted application that uses the big_key data type.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.7
- http://www.securityfocus.com/bid/94546
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7df3e59c3d1df4f87fe874c7956ef7a3d2f4d5fb
- https://github.com/torvalds/linux/commit/7df3e59c3d1df4f87fe874c7956ef7a3d2f4d5fb
- http://www.openwall.com/lists/oss-security/2016/07/22/1
