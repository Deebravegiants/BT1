# [H] ptp: ptp_s390: Add missing facility check

## Summary
Severity: High
Advisory: CVE-2026-68134
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68134
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptp: ptp_s390: Add missing facility check

Only register the physical clock when facility 28 is installed
and PTFF QAF returns that PTFF QPT is available.

## References
- https://git.kernel.org/stable/c/545a7fdbc110c82933d448db2695abff07536f08
- https://git.kernel.org/stable/c/b3efb4744abf493c9782eae713b861a80d9bbeca
- https://git.kernel.org/stable/c/e78f1ac37afcb16cb6fef8a2c92591eab6558956
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68134.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68134
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
