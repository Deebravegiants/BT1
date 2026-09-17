# [H] bnxt_en : Fix memory out-of-bounds in bnxt_fill_hw_rss_tbl()

## Summary
Severity: High
Advisory: CVE-2024-44933
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-44933
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.4 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt_en : Fix memory out-of-bounds in bnxt_fill_hw_rss_tbl()

A recent commit has modified the code in __bnxt_reserve_rings() to
set the default RSS indirection table to default only when the number
of RX rings is changing.  While this works for newer firmware that
requires RX ring reservations, it causes the regression on older
firmware not requiring RX ring resrvations (BNXT_NEW_RM() returns
false).

With older firmware, RX ring reservations are not required and so
hw_resc->resv_rx_rings is not always set to the proper value.  The
comparison:

if (old_rx_rings != bp->hw_resc.resv_rx_rings)

in __bnxt_reserve_rings() may be false even when the RX rings are
changing.  This will cause __bnxt_reserve_rings() to skip setting
the default RSS indirection table to default to match the current
number of RX rings.  This may later cause bnxt_fill_hw_rss_tbl() to
use an out-of-range index.

We already have bnxt_check_rss_tbl_no_rmgr() to handle exactly this
scenario.  We just need to move it up in bnxt_need_reserve_rings()
to be called unconditionally when using older firmware.  Without the
fix, if the TX rings are changing, we'll skip the
bnxt_check_rss_tbl_no_rmgr() call and __bnxt_reserve_rings() may also
skip the bnxt_set_dflt_rss_indir_tbl() call for the reason explained
in the last paragraph.  Without setting the default RSS indirection
table to default, it causes the regression:

BUG: KASAN: slab-out-of-bounds in __bnxt_hwrm_vnic_set_rss+0xb79/0xe40
Read of size 2 at addr ffff8881c5809618 by task ethtool/31525
Call Trace:
__bnxt_hwrm_vnic_set_rss+0xb79/0xe40
 bnxt_hwrm_vnic_rss_cfg_p5+0xf7/0x460
 __bnxt_setup_vnic_p5+0x12e/0x270
 __bnxt_open_nic+0x2262/0x2f30
 bnxt_open_nic+0x5d/0xf0
 ethnl_set_channels+0x5d4/0xb30
 ethnl_default_set_doit+0x2f1/0x620

## References
- https://git.kernel.org/stable/c/abd573e9ad2ba64eaa6418a5f4eec819de28f205
- https://git.kernel.org/stable/c/da03f5d1b2c319a2b74fe76edeadcd8fa5f44376
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44933.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44933
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
