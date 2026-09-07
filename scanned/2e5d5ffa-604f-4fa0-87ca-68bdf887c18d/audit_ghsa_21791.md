# [H] CRLF Injection in microweber

## Summary
Severity: High
Advisory: GHSA-3wwj-wh2w-g4xp
CVE: CVE-2022-0666
CWE: CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-19
Source: https://github.com/advisories/GHSA-3wwj-wh2w-g4xp
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.2.11

## Details
CRLF Injection leads to Stack Trace Exposure due to lack of filtering at https://demo.microweber.org/ in Packagist microweber/microweber prior to 1.2.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0666
- https://github.com/microweber/microweber/commit/f0e338f1b7dc5ec9d99231f4ed3fa6245a5eb128
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/7215afc7-9133-4749-8e8e-0569317dbd55
