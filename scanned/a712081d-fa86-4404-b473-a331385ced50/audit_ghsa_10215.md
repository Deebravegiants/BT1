# [M] Casdoor vulnerable to SSRF via crafted Webhook URL

## Summary
Severity: Medium
Advisory: GHSA-p8c7-hjc4-gwf8
CVE: CVE-2026-5469
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-p8c7-hjc4-gwf8
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
A weakness has been identified in Casdoor 2.356.0. This vulnerability affects unknown code of the component Webhook URL Handler. Executing a manipulation can lead to server-side request forgery. The attack can be launched remotely. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5469
- https://github.com/casdoor/casdoor
- https://vuldb.com/submit/781771
- https://vuldb.com/vuln/355073
- https://vuldb.com/vuln/355073/cti
