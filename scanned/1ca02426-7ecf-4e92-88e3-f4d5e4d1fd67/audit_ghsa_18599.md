# [M] CKAN vulnerable to fixed session IDs

## Summary
Severity: Medium
Advisory: GHSA-2hvh-cw5c-8q8q
CVE: CVE-2025-64100
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-2hvh-cw5c-8q8q
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=2.10.0 <2.10.9
- PyPI: `ckan` — affected >=2.11.0 <2.11.4

## Details
### Impact

Session ids could be fixed by an attacker if the site is configured with server-side session storage (CKAN uses cookie-based session storage by default). The attacker would need to either set a cookie on the victim's browser or steal the victim's currently valid session. Session identifiers are now regenerated after each login.

### Patches
This vulnerability has been fixed in CKAN 2.10.9 and 2.11.4

### References
[https://en.wikipedia.org/wiki/Session_fixation](https://en.wikipedia.org/wiki/Session_fixation)

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-2hvh-cw5c-8q8q
- https://nvd.nist.gov/vuln/detail/CVE-2025-64100
- https://github.com/ckan/ckan/commit/c2fe437f88be850a6edf7a32470772428819fab5
- https://github.com/ckan/ckan
