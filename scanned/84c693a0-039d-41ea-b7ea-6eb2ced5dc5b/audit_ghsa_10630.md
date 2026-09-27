# [M] CKAN has no certificate validation on STMP connection

## Summary
Severity: Medium
Advisory: GHSA-mpfm-fpgx-647q
CVE: CVE-2026-41132
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-mpfm-fpgx-647q
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=2.11.0 <2.11.5
- PyPI: `ckan` — affected >=0 <2.10.10

## Details
### Impact
Configured SMTP server may be spoofed with any certificate (e.g. self-signed), leaving credentials and all emails sent open to MITM attacks.

### Patches
The vulnerability has been patched in CKAN 2.10.10 and CKAN 2.11.5

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-mpfm-fpgx-647q
- https://nvd.nist.gov/vuln/detail/CVE-2026-41132
- https://docs.ckan.org/en/2.10/changelog.html#v-2-10-10-2026-04-29
- https://docs.ckan.org/en/2.11/changelog.html#v-2-11-5-2026-04-29
- https://github.com/ckan/ckan
