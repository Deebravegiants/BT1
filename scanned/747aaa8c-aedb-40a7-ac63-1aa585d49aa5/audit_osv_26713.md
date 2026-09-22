# [H] drm/i915/perf: add sentinel to xehp_oa_b_counters

## Summary
Severity: High
Advisory: CVE-2023-53646
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53646
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/perf: add sentinel to xehp_oa_b_counters

Arrays passed to reg_in_range_table should end with empty record.

The patch solves KASAN detected bug with signature:
BUG: KASAN: global-out-of-bounds in xehp_is_valid_b_counter_addr+0x2c7/0x350 [i915]
Read of size 4 at addr ffffffffa1555d90 by task perf/1518

CPU: 4 PID: 1518 Comm: perf Tainted: G U 6.4.0-kasan_438-g3303d06107f3+ #1
Hardware name: Intel Corporation Meteor Lake Client Platform/MTL-P DDR5 SODIMM SBS RVP, BIOS MTLPFWI1.R00.3223.D80.2305311348 05/31/2023
Call Trace:
<TASK>
...
xehp_is_valid_b_counter_addr+0x2c7/0x350 [i915]

(cherry picked from commit 2f42c5afb34b5696cf5fe79e744f99be9b218798)

## References
- https://git.kernel.org/stable/c/21d92025e80629fd5c25cd6751f8cf38c784dd4a
- https://git.kernel.org/stable/c/785b3f667b4bf98804cad135005e964df0c750de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53646.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53646
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
