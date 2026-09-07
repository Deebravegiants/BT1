# [M] YiiCMS Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gqr4-cvf4-3957
CVE: CVE-2020-21246
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-gqr4-cvf4-3957
Type: github-advisory

## Affected
- Packagist: `sheng/yiicms` — affected >=0 <1.2.1

## Details
Cross Site Scripting vulnerability in YiiCMS v.1.2.0 and prior allows a remote attacker to execute arbitrary code via the news function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-21246
- https://github.com/yongshengli/yiicms/issues/6
- https://github.com/yongshengli/yiicms/commit/4a9d68564eb78d9f64e3f5dd77186a154093615b
- https://github.com/yongshengli/yiicms
