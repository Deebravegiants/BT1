# [M] Filament: Timing-based user enumeration on login page

## Summary
Severity: Medium
Advisory: GHSA-5w46-g9pq-wh6f
CVE: CVE-2026-48166
CWE: CWE-208
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-5w46-g9pq-wh6f
Type: github-advisory

## Affected
- Packagist: `filament/filament` — affected >=4.0.0 <4.11.5
- Packagist: `filament/filament` — affected >=5.0.0 <5.6.5

## Details
The login page has an observable timing discrepancy that allows unauthenticated attackers to enumerate registered email addresses. The impact is limited to disclosing whether an account exists for a given email.

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-5w46-g9pq-wh6f
- https://nvd.nist.gov/vuln/detail/CVE-2026-48166
- https://github.com/filamentphp/filament
