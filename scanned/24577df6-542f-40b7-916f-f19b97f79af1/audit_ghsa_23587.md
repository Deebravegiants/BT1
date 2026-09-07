# [M] MODX Revolution XSS via HTTP Host header

## Summary
Severity: Medium
Advisory: GHSA-p2j4-vrgx-96qg
CVE: CVE-2017-9071
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p2j4-vrgx-96qg
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.5.7

## Details
In MODX Revolution before 2.5.7, an attacker might be able to trigger XSS by injecting a payload into the HTTP Host header of a request. This is exploitable only in conjunction with other issues such as Cache Poisoning.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9071
- https://github.com/modxcms/revolution/pull/13426
- https://citadelo.com/en/2017/04/modx-revolution-cms
- https://github.com/modxcms/revolution
