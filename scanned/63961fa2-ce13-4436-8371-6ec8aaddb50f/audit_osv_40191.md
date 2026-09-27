# [M] CVE-2026-50738

## Summary
Severity: Medium
Advisory: CVE-2026-50738
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-50738
Type: osv

## Details
A use-after-free condition exists in pglogical's worker signaling code, where a worker structure can be dereferenced after the underlying slot has been freed or recycled during normal worker lifecycle events. The condition is reachable during normal replication operation, including by a low-privileged user able to influence worker start, stop, and restart timing through permitted pglogical operations. In the typical case the condition crashes replication workers, causing an availability impact. In the worst case a use-after-free in a PostgreSQL backend can be leveraged as a remote code execution primitive at the privilege of that backend.

## References
- https://www.enterprisedb.com/docs/security/advisories/cve202650738/
