# [H] Guest Entries Remote code execution via file uploads

## Summary
Severity: High
Advisory: GHSA-rw82-mhmx-grmj
CVE: CVE-2023-47621
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-rw82-mhmx-grmj
Type: github-advisory

## Affected
- Packagist: `duncanmcclean/guest-entries` — affected >=0 <3.1.2
- Packagist: `doublethreedigital/guest-entries` — affected >=0 <3.1.2

## Details
### Impact
When using the file uploads feature, it was possible to upload PHP files.

### Patches
The vulnerability is fixed in v3.1.2.

## References
- https://github.com/duncanmcclean/guest-entries/security/advisories/GHSA-rw82-mhmx-grmj
- https://nvd.nist.gov/vuln/detail/CVE-2023-47621
- https://github.com/duncanmcclean/guest-entries/commit/a8e17b4413bfbbc337a887761a6c858ef1ddb4da
- https://github.com/duncanmcclean/guest-entries
