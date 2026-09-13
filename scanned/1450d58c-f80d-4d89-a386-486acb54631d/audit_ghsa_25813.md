# [C] Type Confusion in ImpressCMS

## Summary
Severity: Critical
Advisory: GHSA-m8xh-cqc2-5q6f
CVE: CVE-2021-26600
CWE: CWE-843
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-29
Source: https://github.com/advisories/GHSA-m8xh-cqc2-5q6f
Type: github-advisory

## Affected
- Packagist: `impresscms/impresscms` — affected >=0 <1.4.3

## Details
ImpressCMS before 1.4.3 has plugins/preloads/autologin.php type confusion with resultant Authentication Bypass (!= instead of !==).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26600
- https://hackerone.com/reports/1081986
- https://github.com/ImpressCMS/impresscms
- https://github.com/ImpressCMS/impresscms/releases/tag/v1.4.3
- http://karmainsecurity.com/KIS-2022-01
- http://packetstormsecurity.com/files/166393/ImpressCMS-1.4.2-Authentication-Bypass.html
- http://seclists.org/fulldisclosure/2022/Mar/43
