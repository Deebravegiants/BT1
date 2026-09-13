# [C] XML External Entity vulnerability in MODX CMS

## Summary
Severity: Critical
Advisory: GHSA-vhfp-9wvj-gwvg
CVE: CVE-2020-25911
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-01
Source: https://github.com/advisories/GHSA-vhfp-9wvj-gwvg
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.8.0

## Details
A XML External Entity (XXE) vulnerability was discovered in the modRestServiceRequest component in MODX CMS 2.7.3 which can lead to an information disclosure or denial of service (DOS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25911
- https://github.com/modxcms/revolution/issues/15237
- https://github.com/modxcms/revolution/pull/15238
- https://github.com/modxcms/revolution/pull/15238/commits/1b7ffe02df30f05dbf67dd15e4d8101687c1585a
- https://github.com/dahua966/Vul_disclose/blob/main/XXE_modxcms.md
- https://github.com/modxcms/revolution
