# [M] ansi_up cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2v5f-23xc-v9qr
CVE: CVE-2021-3377
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-11
Source: https://github.com/advisories/GHSA-2v5f-23xc-v9qr
Type: github-advisory

## Affected
- npm: `ansi_up` — affected >=0 <5.0.0

## Details
The npm package ansi_up converts ANSI escape codes into HTML. In ansi_up v4, ANSI escape codes can be used to create HTML hyperlinks. Due to insufficient URL sanitization, this feature is affected by a cross-site scripting (XSS) vulnerability. This issue is fixed in v5.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3377
- https://github.com/drudru/ansi_up/commit/c8c726ed1db979bae4f257b7fa41775155ba2e27
- https://doyensec.com/resources/Doyensec_Advisory_ansi_up4_XSS.pdf
- https://security.netapp.com/advisory/ntap-20241108-0002
