# [M] RustFS: Authentication bypass in /profile/cpu and /profile/memory allows unauthenticated access to profiling handlers

## Summary
Severity: Medium
Advisory: CVE-2026-45044
Aliases: GHSA-8784-9m7f-c6p6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45044
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.2, the admin router explicitly whitelists /profile/cpu and /profile/memory from the authentication layer, allowing any unauthenticated HTTP client to invoke profiling handlers without credentials. On supported builds (e.g., glibc), the handler invokes a fixed 60-second CPU profiling operation (dump_cpu_pprof_for(Duration::from_secs(60))). This may result in significant CPU resource consumption per request and can potentially lead to denial of service when abused. Additionally, the handler returns the server’s absolute filesystem path in the response body, resulting in information disclosure. This vulnerability is fixed in 1.0.0-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45044.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-8784-9m7f-c6p6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45044
