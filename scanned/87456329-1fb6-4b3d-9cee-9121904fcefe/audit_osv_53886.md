# [M] CVE-2023-30772

## Summary
Severity: Medium
Advisory: CVE-2023-30772
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2023-30772
Type: osv

## Details
The Linux kernel before 6.2.9 has a race condition and resultant use-after-free in drivers/power/supply/da9150-charger.c if a physically proximate attacker unplugs a device.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://bugzilla.suse.com/show_bug.cgi?id=1210329
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.9
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=06615d11cc78162dfd5116efb71f29eb29502d37
