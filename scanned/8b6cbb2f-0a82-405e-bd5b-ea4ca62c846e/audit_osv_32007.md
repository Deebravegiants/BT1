# [H] ice: validate queue quanta parameters to prevent OOB access

## Summary
Severity: High
Advisory: CVE-2025-22118
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22118
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: validate queue quanta parameters to prevent OOB access

Add queue wraparound prevention in quanta configuration.
Ensure end_qid does not overflow by validating start_qid and num_queues.

## References
- https://git.kernel.org/stable/c/4161cf3f4c11006507f4e02bedc048a215a4b81a
- https://git.kernel.org/stable/c/e2f7d3f7331b92cb820da23e8c45133305da1e63
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22118.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22118
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
