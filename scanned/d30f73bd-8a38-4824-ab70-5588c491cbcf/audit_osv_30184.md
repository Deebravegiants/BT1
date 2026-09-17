# [H] RDMA/bnxt_re: Fix out of bound check

## Summary
Severity: High
Advisory: CVE-2024-50158
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50158
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Fix out of bound check

Driver exports pacing stats only on GenP5 and P7 adapters. But while
parsing the pacing stats, driver has a check for "rdev->dbr_pacing".  This
caused a trace when KASAN is enabled.

BUG: KASAN: slab-out-of-bounds in bnxt_re_get_hw_stats+0x2b6a/0x2e00 [bnxt_re]
Write of size 8 at addr ffff8885942a6340 by task modprobe/4809

## References
- https://git.kernel.org/stable/c/05c5fcc1869a08e36a29691699b6534e5a00a82b
- https://git.kernel.org/stable/c/a9e6e7443922ac0a48243c35d03834c96926bff1
- https://git.kernel.org/stable/c/c11b9b03ea5252898f91f3388c248f0dc47bda52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50158.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50158
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
