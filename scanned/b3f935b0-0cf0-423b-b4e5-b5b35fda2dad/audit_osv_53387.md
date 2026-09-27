# [M] CVE-2022-41850

## Summary
Severity: Medium
Advisory: CVE-2022-41850
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-30
Source: https://osv.dev/vulnerability/CVE-2022-41850
Type: osv

## Details
roccat_report_event in drivers/hid/hid-roccat.c in the Linux kernel through 5.19.12 has a race condition and resultant use-after-free in certain situations where a report is received while copying a report->value is in progress.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cacdb14b1c8d3804a3a7d31773bc7569837b71a4
- https://lore.kernel.org/all/20220904193115.GA28134%40ubuntu/t/#u
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
