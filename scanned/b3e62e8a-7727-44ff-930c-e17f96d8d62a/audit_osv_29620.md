# [H] net: ethernet: mtk_wed: fix use-after-free panic in mtk_wed_setup_tc_block_cb()

## Summary
Severity: High
Advisory: CVE-2024-44997
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44997
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: mtk_wed: fix use-after-free panic in mtk_wed_setup_tc_block_cb()

When there are multiple ap interfaces on one band and with WED on,
turning the interface down will cause a kernel panic on MT798X.

Previously, cb_priv was freed in mtk_wed_setup_tc_block() without
marking NULL,and mtk_wed_setup_tc_block_cb() didn't check the value, too.

Assign NULL after free cb_priv in mtk_wed_setup_tc_block() and check NULL
in mtk_wed_setup_tc_block_cb().

----------
Unable to handle kernel paging request at virtual address 0072460bca32b4f5
Call trace:
 mtk_wed_setup_tc_block_cb+0x4/0x38
 0xffffffc0794084bc
 tcf_block_playback_offloads+0x70/0x1e8
 tcf_block_unbind+0x6c/0xc8
...
---------

## References
- https://git.kernel.org/stable/c/326a89321f9d5fe399fe6f9ff7c0fc766582a6a0
- https://git.kernel.org/stable/c/b453a4bbda03aa8741279c360ac82d1c3ac33548
- https://git.kernel.org/stable/c/db1b4bedb9b97c6d34b03d03815147c04fffe8b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44997.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44997
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
