# [M] Incorrect Access Control in ImpressCMS

## Summary
Severity: Medium
Advisory: GHSA-48p3-xfvw-g59c
CVE: CVE-2021-26598
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-29
Source: https://github.com/advisories/GHSA-48p3-xfvw-g59c
Type: github-advisory

## Affected
- Packagist: `impresscms/impresscms` — affected >=0 <1.4.3

## Details
ImpressCMS before 1.4.3 has Incorrect Access Control because include/findusers.php allows access by unauthenticated attackers (who are, by design, able to have a security token).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26598
- https://github.com/ImpressCMS/impresscms/pull/967
- https://hackerone.com/reports/1081137
- https://github.com/ImpressCMS/impresscms
- https://github.com/ImpressCMS/impresscms/releases/tag/v1.4.3
- https://packetstormsecurity.com/files/166403/ImpressCMS-1.4.2-Incorrect-Access-Control.html
- http://karmainsecurity.com/KIS-2022-03
- http://seclists.org/fulldisclosure/2022/Mar/45
