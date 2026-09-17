# [M] CVE-2025-47711

## Summary
Severity: Medium
Advisory: CVE-2025-47711
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-47711
Type: osv

## Details
There's a flaw in the nbdkit server when handling responses from its plugins regarding the status of data blocks. If a client makes a specific request for a very large data range, and a plugin responds with an even larger single block, the nbdkit server can encounter a critical internal error, leading to a denial-of-service.

## References
- https://access.redhat.com/security/cve/CVE-2025-47711
- https://bugzilla.redhat.com/show_bug.cgi?id=2365687
