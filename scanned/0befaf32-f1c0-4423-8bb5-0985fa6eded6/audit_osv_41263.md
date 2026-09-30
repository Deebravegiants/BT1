# [M] GPUStack Unauthenticated Information Disclosure via Worker Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-58658
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-58658
Type: osv

## Details
GPUStack through 2.2.1, fixed in commit 4e20551, contains an unauthenticated information disclosure vulnerability that allows unauthenticated attackers to access sensitive inference logs and modify worker configuration by exploiting unprotected /serveLogs and /debug endpoints on the worker port. Attackers can enumerate model instance IDs to stream serving logs containing prompts and completions, change log levels, and read memory profiling data without any authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58658.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58658
- https://www.vulncheck.com/advisories/gpustack-unauthenticated-information-disclosure-via-worker-endpoints
- https://github.com/gpustack/gpustack/commit/4e20551b5aaf76f93a8769d32b7fef999e22a4d3
- https://github.com/gpustack/gpustack
- https://github.com/gpustack/gpustack/issues/5836
