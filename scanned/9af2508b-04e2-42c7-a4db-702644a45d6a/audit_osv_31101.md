# [M] rtc: tps6594: Fix integer overflow on 32bit systems

## Summary
Severity: Medium
Advisory: CVE-2024-57953
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57953
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtc: tps6594: Fix integer overflow on 32bit systems

The problem is this multiply in tps6594_rtc_set_offset()

	tmp = offset * TICKS_PER_HOUR;

The "tmp" variable is an s64 but "offset" is a long in the
(-277774)-277774 range.  On 32bit systems a long can hold numbers up to
approximately two billion.  The number of TICKS_PER_HOUR is really large,
(32768 * 3600) or roughly a hundred million.  When you start multiplying
by a hundred million it doesn't take long to overflow the two billion
mark.

Probably the safest way to fix this is to change the type of
TICKS_PER_HOUR to long long because it's such a large number.

## References
- https://git.kernel.org/stable/c/09c4a610153286cef54d4f0c85398f4e32fc227e
- https://git.kernel.org/stable/c/5127f3cbfc78a7b301b86328247230bec47e0bb3
- https://git.kernel.org/stable/c/53b0c7b15accb18d15d95c7fe68f61630ebfd1ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57953.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57953
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
