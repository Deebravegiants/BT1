# [M] Elastic Package Registry has Improper Verification of Cryptographic Signature 

## Summary
Severity: Medium
Advisory: GHSA-r727-5pf6-47r2
CVE: CVE-2026-33467
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-r727-5pf6-47r2
Type: github-advisory

## Affected
- Go: `github.com/elastic/package-registry` — affected >=0 <1.38.0

## Details
Improper Verification of Cryptographic Signature (CWE-347) in Elastic Package Registry could allow an attacker positioned to intercept network traffic, or to otherwise influence the contents served to a self-hosted registry, to substitute a tampered package without the integrity check failing closed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33467
- https://discuss.elastic.co/t/elastic-package-registry-1-38-0-security-update-esa-2026-27/386081
- https://github.com/elastic/package-registry
