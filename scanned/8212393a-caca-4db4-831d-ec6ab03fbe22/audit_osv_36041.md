# [M] Denial of Service via Unbounded Recursion in go-attestation Windows SIPA Parser

## Summary
Severity: Medium
Advisory: CVE-2026-19201
Aliases: GHSA-hcm6-rjfh-f25p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-19201
Type: osv

## Details
An uncontrolled recursion vulnerability in the Windows SIPA event log parser of Google go-attestation versions up to and including 0.6.1 allows an attacker to cause a denial of service (DoS). The (*WinEvents).readELAMAggregation function recurses for every nested elamAggregation sub-event without enforcing a maximum recursion depth limit, while the size guard is bypassed on recursive execution paths. By submitting a crafted Windows event log containing deeply nested elamAggregation headers, an attacker can exhaust the goroutine call stack, triggering an unrecoverable fatal runtime error (stack overflow) that immediately crashes the verifier application.

## References
- https://github.com/google/go-attestation/releases/tag/v0.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19201.json
- https://github.com/google/go-attestation/security/advisories/GHSA-hcm6-rjfh-f25p
- https://nvd.nist.gov/vuln/detail/CVE-2026-19201
- https://github.com/google/go-attestation/pull/506
