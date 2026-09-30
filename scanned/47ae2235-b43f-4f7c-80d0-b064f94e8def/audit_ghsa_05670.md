# [C] Free5gc NRF is vulnerable to scope validation bypass via maliciously crafted targetNF value

## Summary
Severity: Critical
Advisory: GHSA-q7c8-gfjh-8v4p
CVE: CVE-2025-66719
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-q7c8-gfjh-8v4p
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nrf` — affected >=0 <1.4.1

## Details
An issue was discovered in Free5gc NRF 1.4.0. In the access-token generation logic of free5GC, the AccessTokenScopeCheck() function in file internal/sbi/processor/access_token.go bypasses all scope validation when the attacker uses a crafted targetNF value. This allows attackers to obtain an access token with any arbitrary scope.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66719
- https://github.com/free5gc/free5gc/issues/733
- https://github.com/free5gc/free5gc/issues/736
- https://github.com/free5gc/nrf/pull/73
- https://github.com/free5gc/nrf
