# [M] Free5GC is vulnerable to DoS via the Nudm_SubscriberDataManagement API

## Summary
Severity: Medium
Advisory: GHSA-3j9f-7w24-pcqg
CVE: CVE-2025-60633
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-3j9f-7w24-pcqg
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udm` — affected >=0
- Go: `github.com/free5gc/openapi` — affected >=0 <1.2.2

## Details
An issue was discovered in Free5GC v4.0.0 and v4.0.1 allowing an attacker to cause a denial of service via the Nudm_SubscriberDataManagement API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60633
- https://github.com/free5gc/free5gc/issues/700
- https://github.com/free5gc/free5gc/issues/701
- https://github.com/free5gc/free5gc/issues/702
- https://github.com/free5gc/free5gc/issues/703
- https://github.com/free5gc/openapi/pull/65
- https://github.com/free5gc/udm/pull/63
- https://github.com/free5gc/udm/pull/65
- https://github.com/free5gc/udm/pull/66
- https://github.com/free5gc/openapi/commit/d50c83e8fe7ebf9a62d9de99517e21a17f627b52
- https://github.com/free5gc/udm/commit/57c56a3ad4bc53a62cab259045e78ec9abdb98ca
- https://github.com/free5gc/udm/commit/ca9976857909a422dcff5bf2228756fc2bfc80d1
- https://github.com/free5gc/udm/commit/e776c42177817f75e75e7a587c58c2a027beed81
- https://github.com/advisories/GHSA-3j9f-7w24-pcqg
- https://github.com/free5gc/pcf
