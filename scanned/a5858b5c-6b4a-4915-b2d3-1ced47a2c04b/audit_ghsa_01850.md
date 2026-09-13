# [C] SQL Injection in rosariosis

## Summary
Severity: Critical
Advisory: GHSA-wf5p-f5xr-c4jj
CVE: CVE-2021-44427
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-wf5p-f5xr-c4jj
Type: github-advisory

## Affected
- Packagist: `francoisjacquet/rosariosis` — affected >=0 <8.1.1

## Details
An unauthenticated SQL Injection vulnerability in Rosario Student Information System (aka rosariosis) before 8.1.1 allows remote attackers to execute PostgreSQL statements (e.g., SELECT, INSERT, UPDATE, and DELETE) through /Side.php via the syear parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44427
- https://github.com/francoisjacquet/rosariosis/commit/e001430aa9fb53d2502fb6f036f6c51c578d2016
- https://github.com/francoisjacquet/rosariosis
- https://gitlab.com/francoisjacquet/rosariosis/-/commit/e001430aa9fb53d2502fb6f036f6c51c578d2016
- https://gitlab.com/francoisjacquet/rosariosis/-/issues/328
- https://gitlab.com/francoisjacquet/rosariosis/blob/mobile/CHANGES.md#changes-in-811
