# [H] CVE-2023-3141

## Summary
Severity: High
Advisory: CVE-2023-3141
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-06-09
Source: https://osv.dev/vulnerability/CVE-2023-3141
Type: osv

## Details
A use-after-free flaw was found in r592_remove in drivers/memstick/host/r592.c in media access in the Linux Kernel. This flaw allows a local attacker to crash the system at device disconnect, possibly leading to a kernel information leak.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=63264422785021704c39b38f65a78ab9e4a186d7
- https://lore.kernel.org/lkml/CAPDyKFoV9aZObZ5GBm0U_-UVeVkBN_rAG-kH3BKoP4EXdYM4bw%40mail.gmail.com/t/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3141.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3141
- https://security.netapp.com/advisory/ntap-20230706-0004/
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
