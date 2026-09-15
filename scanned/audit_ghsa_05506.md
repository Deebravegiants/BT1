# [M] jsonrpc4j has Infinite Loop in RPC Stream Writer 

## Summary
Severity: Medium
Advisory: GHSA-hcx3-3q5c-r5v6
CVE: CVE-2026-24802
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:L/SC:N/SI:N/SA:L/AU:Y/R:A/V:D/RE:M/U:Amber (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-hcx3-3q5c-r5v6
Type: github-advisory

## Affected
- Maven: `com.github.briandilley.jsonrpc4j:jsonrpc4j` — affected >=0 <1.7.0

## Details
Loop with Unreachable Exit Condition ('Infinite Loop') vulnerability in briandilley jsonrpc4j (src/main/java/com/googlecode/jsonrpc4j modules). This vulnerability is associated with program files NoCloseOutputStream.Java.

This issue affects jsonrpc4j: through 1.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24802
- https://github.com/briandilley/jsonrpc4j/pull/333
- https://github.com/briandilley/jsonrpc4j/commit/087f5268eaf901f90d1e84062def77faa52ad8b2
- https://github.com/briandilley/jsonrpc4j
