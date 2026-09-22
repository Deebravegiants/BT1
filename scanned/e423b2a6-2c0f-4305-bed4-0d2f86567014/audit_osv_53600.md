# [M] CVE-2023-0459

## Summary
Severity: Medium
Advisory: CVE-2023-0459
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-0459
Type: osv

## Details
Copy_from_user on 64-bit versions of the Linux kernel does not implement the __uaccess_begin_nospec allowing a user to bypass the "access_ok" check and pass a kernel pointer to copy_from_user(). This would allow an attacker to leak information. We recommend upgrading beyond commit 74e19ef0ff8061ef55957c3abd71614ef0f42f47

## References
- https://github.com/torvalds/linux/commit/74e19ef0ff8061ef55957c3abd71614ef0f42f47
- https://github.com/torvalds/linux/commit/4b842e4e25b12951fa10dedb4bc16bc47e3b850c
