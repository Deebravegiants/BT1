# [M] XSS vulnerability on email template preview page

## Summary
Severity: Medium
Advisory: GHSA-qv7g-j98v-8pp7
CVE: CVE-2021-41236
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-qv7g-j98v-8pp7
Type: github-advisory

## Affected
- Packagist: `oro/platform` — affected >=3.1.0 <3.1.21
- Packagist: `oro/platform` — affected >=4.1.0 <4.1.14
- Packagist: `oro/platform` — affected >=4.2.0 <4.2.8

## Details
### Summary

Email template preview is vulnerable to XSS payload added to email template content. The attacker should have permission to create or edit an email template. For successful payload, execution attacked user should preview a vulnerable email template.

### Workarounds

There are no workarounds that address this vulnerability.

## References
- https://github.com/oroinc/platform/security/advisories/GHSA-qv7g-j98v-8pp7
- https://nvd.nist.gov/vuln/detail/CVE-2021-41236
- https://github.com/oroinc/platform/commit/2a089c971fc70bc63baf8770d29ee515ce5a415a
- https://github.com/oroinc/platform
