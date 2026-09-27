# [M] RustFS: Missing admin authorization on /rustfs/admin/v3/metrics allows any authenticated user to read server metrics

## Summary
Severity: Medium
Advisory: CVE-2026-55838
Aliases: GHSA-f5cv-v44x-2xgf
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-55838
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. In 1.0.0-beta.7 and earlier, the real-time metrics endpoint at /rustfs/admin/v3/metrics is accessible to any valid IAM user regardless of their assigned policy. Every other admin handler in the codebase calls validate_admin_request to enforce admin-action IAM checks; the MetricsHandler skips this call entirely. A restricted IAM user whose policy grants only access to their own bucket can read server-wide operational metrics including disk I/O statistics, network throughput, scanner cycle timing, and cluster RPC state.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55838.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-f5cv-v44x-2xgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-55838
