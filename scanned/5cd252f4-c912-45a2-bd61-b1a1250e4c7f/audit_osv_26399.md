# [H] ntb_hw_switchtec: Fix shift-out-of-bounds in switchtec_ntb_mw_set_trans

## Summary
Severity: High
Advisory: CVE-2023-53034
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2023-53034
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntb_hw_switchtec: Fix shift-out-of-bounds in switchtec_ntb_mw_set_trans

There is a kernel API ntb_mw_clear_trans() would pass 0 to both addr and
size. This would make xlate_pos negative.

[   23.734156] switchtec switchtec0: MW 0: part 0 addr 0x0000000000000000 size 0x0000000000000000
[   23.734158] ================================================================================
[   23.734172] UBSAN: shift-out-of-bounds in drivers/ntb/hw/mscc/ntb_hw_switchtec.c:293:7
[   23.734418] shift exponent -1 is negative

Ensuring xlate_pos is a positive or zero before BIT.

## References
- https://git.kernel.org/stable/c/0df2e03e4620548b41891b4e0d1bd9d2e0d8a39a
- https://git.kernel.org/stable/c/2429bdf26a0f3950fdd996861e9c1a3873af1dbe
- https://git.kernel.org/stable/c/36d32cfb00d42e865396424bb5d340fc0a28870d
- https://git.kernel.org/stable/c/5b6857bb3bfb0dae17fab1e42c1e82c204a508b1
- https://git.kernel.org/stable/c/7ed22f8d8be26225a78cf5e85b2036421a6bf2d5
- https://git.kernel.org/stable/c/c61a3f2df162ba424be0141649a9ef5f28eaccc1
- https://git.kernel.org/stable/c/cb153bdc1812a3375639ed6ca5f147eaefb65349
- https://git.kernel.org/stable/c/de203da734fae00e75be50220ba5391e7beecdf9
- https://git.kernel.org/stable/c/f56951f211f181410a383d305e8d370993e45294
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53034.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53034
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
