# [M] Temporal OSS Server Vulnerable to Allocation of Resources Without Limits or Throttling

## Summary
Severity: Medium
Advisory: GHSA-p768-c3pr-6459
CVE: CVE-2025-8396
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-p768-c3pr-6459
Type: github-advisory

## Affected
- Go: `go.temporal.io/server` — affected >=0 <1.26.3
- Go: `go.temporal.io/server` — affected >=1.27.0-126.0 <1.27.3
- Go: `go.temporal.io/server` — affected >=1.28.0-129.0 <1.28.1

## Details
Insufficiently specific bounds checking on authorization header could lead to denial of service in the Temporal server on all platforms due to excessive memory allocation. This issue affects all platforms and versions of OSS Server prior to 1.26.3, 1.27.3, and 1.28.1 (i.e., fixed in 1.26.3, 1.27.3, and 1.28.1 and later). Temporal Cloud services are not impacted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8396
- https://github.com/temporalio/temporal
- https://github.com/temporalio/temporal/releases/tag/v1.26.3
- https://github.com/temporalio/temporal/releases/tag/v1.27.3
- https://github.com/temporalio/temporal/releases/tag/v1.28.1
