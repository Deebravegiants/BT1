# [H] drm: adv7511: Fix use-after-free in adv7533_attach_dsi()

## Summary
Severity: High
Advisory: CVE-2024-57887
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57887
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.234, >=5.11.0 <6.1.125, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: adv7511: Fix use-after-free in adv7533_attach_dsi()

The host_node pointer was assigned and freed in adv7533_parse_dt(), and
later, adv7533_attach_dsi() uses the same. Fix this use-after-free issue
by dropping of_node_put() in adv7533_parse_dt() and calling of_node_put()
in error path of probe() and also in the remove().

## References
- https://git.kernel.org/stable/c/1f49aaf55652580ae63ab83d67211fe6a55d83dc
- https://git.kernel.org/stable/c/81adbd3ff21c1182e06aa02c6be0bfd9ea02d8e8
- https://git.kernel.org/stable/c/acec80d9f126cd3fa764bbe3d96bc0cb5cd2b087
- https://git.kernel.org/stable/c/ca9d077350fa21897de8bf64cba23b198740aab5
- https://git.kernel.org/stable/c/d208571943ffddc438a7ce533d5d0b9219806242
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57887.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
