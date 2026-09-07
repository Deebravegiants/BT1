# [M] BentoML Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-564p-rx2q-4c8v
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-564p-rx2q-4c8v
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0

## Details
An open redirect vulnerability in bentoml/bentoml v1.3.9 allows a remote unauthenticated attacker to redirect users to arbitrary websites via a specially crafted URL. This can be exploited for phishing attacks, malware distribution, and credential theft.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4940
- https://github.com/bentoml/BentoML
- https://huntr.com/bounties/2a284ff6-cc6c-4a10-b72e-1bb31c842bca
- https://huntr.com/bounties/35aaea93-6895-4f03-9c1b-cd992665aa60
