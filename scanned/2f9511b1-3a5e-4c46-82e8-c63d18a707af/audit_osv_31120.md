# [H] OPP: add index check to assert to avoid buffer overflow in _read_freq()

## Summary
Severity: High
Advisory: CVE-2024-57998
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57998
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

OPP: add index check to assert to avoid buffer overflow in _read_freq()

Pass the freq index to the assert function to make sure
we do not read a freq out of the opp->rates[] table when called
from the indexed variants:
dev_pm_opp_find_freq_exact_indexed() or
dev_pm_opp_find_freq_ceil/floor_indexed().

Add a secondary parameter to the assert function, unused
for assert_single_clk() then add assert_clk_index() which
will check for the clock index when called from the _indexed()
find functions.

## References
- https://git.kernel.org/stable/c/774dd6f0f0a61c9c3848e025d7d9eeed1a7ca4cd
- https://git.kernel.org/stable/c/7d68c20638e50d5eb4576492a7958328ae445248
- https://git.kernel.org/stable/c/d659bc68ed489022ea33342cfbda2911a81e7a0d
- https://git.kernel.org/stable/c/da2a6acc73933b7812c94794726e438cde39e037
- https://git.kernel.org/stable/c/eb6ffa0192ba83ece1a318b956265519c5c7dcec
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57998.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
