# [C] net: do not pass flow_id to set_rps_cpu()

## Summary
Severity: Critical
Advisory: CVE-2026-43208
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43208
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: do not pass flow_id to set_rps_cpu()

Blamed commit made the assumption that the RPS table for each receive
queue would have the same size, and that it would not change.

Compute flow_id in set_rps_cpu(), do not assume we can use the value
computed by get_rps_cpu(). Otherwise we risk out-of-bound access
and/or crashes.

## References
- https://git.kernel.org/stable/c/5455a232edea6b946b99449f15ca771a8874a5a6
- https://git.kernel.org/stable/c/8a8a9fac9efa6423fd74938b940cb7d731780718
- https://git.kernel.org/stable/c/ed712dc0d64dee5f0d05e4d8ca57711f8a9c850c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43208
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
