# [H] mm/compaction: handle free_pages_prepare() properly in compaction_free()

## Summary
Severity: High
Advisory: CVE-2026-72027
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72027
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/compaction: handle free_pages_prepare() properly in compaction_free()

free_pages_prepare() can fail but compaction_free() does not handle the
failure case.  Failed pages should not be added back to cc->freepages for
future use, since they can be either PageHWPoison or free_page_is_bad()
and might cause data corruption.

## References
- https://git.kernel.org/stable/c/018d7ad26cb8bdfe9842f2ca68a42b0bfdcc82fe
- https://git.kernel.org/stable/c/23afc3786acf359c135093893fb43a436768c832
- https://git.kernel.org/stable/c/7da7d599b8a83271c464adfd5ef160202b470570
- https://git.kernel.org/stable/c/de8577db09039d4950239b01446ab5ead9028ab4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72027.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72027
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
