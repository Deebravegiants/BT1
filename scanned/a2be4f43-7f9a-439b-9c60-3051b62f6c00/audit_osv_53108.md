# [H] CVE-2022-29582

## Summary
Severity: High
Advisory: CVE-2022-29582
Aliases: A-231494876, ASB-A-231494876
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-22
Source: https://osv.dev/vulnerability/CVE-2022-29582
Type: osv

## Details
In the Linux kernel before 5.17.3, fs/io_uring.c has a use-after-free due to a race condition in io_uring timeouts. This can be triggered by a local user who has no access to any user namespace; however, the race condition perhaps can only be exploited infrequently.

## References
- http://www.openwall.com/lists/oss-security/2024/04/24/3
- https://www.debian.org/security/2022/dsa-5127
- http://www.openwall.com/lists/oss-security/2022/08/08/3
- https://github.com/Ruia-ruia/CVE-2022-29582-Exploit
- https://www.openwall.com/lists/oss-security/2022/04/22/3
- http://www.openwall.com/lists/oss-security/2022/04/22/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.3
- https://github.com/torvalds/linux/commit/e677edbcabee849bfdd43f1602bccbecf736a646
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e677edbcabee849bfdd43f1602bccbecf736a646
- https://ruia-ruia.github.io/2022/08/05/CVE-2022-29582-io-uring/
