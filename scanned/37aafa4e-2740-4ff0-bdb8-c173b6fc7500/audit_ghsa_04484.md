# [H] Routinator crashes when sending a maliciously crafted select-asn query parameter

## Summary
Severity: High
Advisory: GHSA-gc6q-cwcj-3vh9
CVE: CVE-2026-49234
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-gc6q-cwcj-3vh9
Type: github-advisory

## Affected
- crates.io: `routinator` — affected >=0 <0.15.2

## Details
When sending a specifically crafted non-UTF-8 string as select-asn query parameter to the /api/v1/origins endpoint, Routinator crashes. 

This only affects users who allow API access from untrusted networks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49234
- https://github.com/NLnetLabs/routinator
- https://github.com/NLnetLabs/routinator/releases/tag/v0.15.2
- https://www.nlnetlabs.nl/downloads/routinator/CVE-2026-49234.txt
