# [C] netfs: Fix missing locking around retry adding new subreqs

## Summary
Severity: Critical
Advisory: CVE-2026-64068
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64068
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.18.50, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix missing locking around retry adding new subreqs

Fix netfs_retry_read_subrequests() and netfs_retry_write_stream() to take
the appropriate lock when adding extra subrequests into
stream->subrequests.

## References
- https://git.kernel.org/stable/c/393f3f0d7353a94b1e0bc4ca89c683fe983e5fd2
- https://git.kernel.org/stable/c/cce18c263e9623872327ba3c956012f73c1179cc
- https://git.kernel.org/stable/c/d5c9d19b0ff2f7153532ac238a5e96fed2df315c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64068.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
