# [M] CVE-2017-18224

## Summary
Severity: Medium
Advisory: CVE-2017-18224
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2017-18224
Type: osv

## Details
In the Linux kernel before 4.15, fs/ocfs2/aops.c omits use of a semaphore and consequently has a race condition for access to the extent tree during read operations in DIRECT mode, which allows local users to cause a denial of service (BUG) by modifying a certain e_cpos field.

## References
- http://www.securityfocus.com/bid/103353
- https://www.debian.org/security/2018/dsa-4188
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3e4c56d41eef5595035872a2ec5a483f42e8917f
- https://github.com/torvalds/linux/commit/3e4c56d41eef5595035872a2ec5a483f42e8917f
