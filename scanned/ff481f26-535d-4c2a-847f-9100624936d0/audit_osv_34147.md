# [M] CVE-2025-55181

## Summary
Severity: Medium
Advisory: CVE-2025-55181
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-12-02
Source: https://osv.dev/vulnerability/CVE-2025-55181
Type: osv

## Details
Sending an HTTP request/response body with greater than 2^31 bytes triggers an infinite loop in proxygen::coro::HTTPQuicCoroSession which blocks the backing event loop and unconditionally appends data to a std::vector per-loop iteration. This issue leads to unbounded memory growth and eventually causes the process to run out of memory.

## References
- https://www.facebook.com/security/advisories/cve-2025-55181
- https://github.com/facebook/proxygen/commit/17689399ef99b7c3d3a8b2b768b1dba1a4b72f8f
