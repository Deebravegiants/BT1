# [M] OPP: fix dev_pm_opp_find_bw_*() when bandwidth table not initialized

## Summary
Severity: Medium
Advisory: CVE-2024-58068
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58068
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

OPP: fix dev_pm_opp_find_bw_*() when bandwidth table not initialized

If a driver calls dev_pm_opp_find_bw_ceil/floor() the retrieve bandwidth
from the OPP table but the bandwidth table was not created because the
interconnect properties were missing in the OPP consumer node, the
kernel will crash with:

Unable to handle kernel NULL pointer dereference at virtual address 0000000000000004
...
pc : _read_bw+0x8/0x10
lr : _opp_table_find_key+0x9c/0x174
...
Call trace:
  _read_bw+0x8/0x10 (P)
  _opp_table_find_key+0x9c/0x174 (L)
  _find_key+0x98/0x168
  dev_pm_opp_find_bw_ceil+0x50/0x88
...

In order to fix the crash, create an assert function to check
if the bandwidth table was created before trying to get a
bandwidth with _read_bw().

## References
- https://git.kernel.org/stable/c/5165486681dbd67b61b975c63125f2a5cb7f96d1
- https://git.kernel.org/stable/c/84ff05c9bd577157baed711a4f0b41206593978b
- https://git.kernel.org/stable/c/8532fd078d2a5286915d03bb0a0893ee1955acef
- https://git.kernel.org/stable/c/b44b9bc7cab2967c3d6a791b1cd542c89fc07f0e
- https://git.kernel.org/stable/c/ff2def251849133be6076a7c2d427d8eb963c223
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58068.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
