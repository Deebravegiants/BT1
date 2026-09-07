# [C] slub_events for Typo3 Arbitrary File Upload

## Summary
Severity: Critical
Advisory: GHSA-5pww-3mfc-g8vr
CVE: CVE-2019-16700
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5pww-3mfc-g8vr
Type: github-advisory

## Affected
- Packagist: `slub/slub-events` — affected >=0 <3.0.3

## Details
The slub_events (aka SLUB: Event Registration) extension through 3.0.2 for TYPO3 allows uploading of arbitrary files to the webserver. For versions 1.2.2 and below, this results in Remote Code Execution. In versions later than 1.2.2, this can result in Denial of Service, since the web space can be filled up with arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16700
- https://extensions.typo3.org/extension/slub_events
- https://typo3.org/security/advisory/typo3-ext-sa-2019-017
