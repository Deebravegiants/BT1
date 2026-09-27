# [M] CVE-2023-33288

## Summary
Severity: Medium
Advisory: CVE-2023-33288
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-22
Source: https://osv.dev/vulnerability/CVE-2023-33288
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.2.9. A use-after-free was found in bq24190_remove in drivers/power/supply/bq24190_charger.c. It could allow a local attacker to crash the system due to a race condition.

## References
- https://lore.kernel.org/all/CAHk-=whcaHLNpb7Mu_QX7ABwPgyRyfW-V8=v4Mv0S22fpjY4JQ%40mail.gmail.com/
- https://lore.kernel.org/lkml/20230309174728.233732-1-zyytlz.wz%40163.com/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.9
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=47c29d69212911f50bdcdd0564b5999a559010d4
- https://github.com/torvalds/linux/commit/47c29d69212911f50bdcdd0564b5999a559010d4
