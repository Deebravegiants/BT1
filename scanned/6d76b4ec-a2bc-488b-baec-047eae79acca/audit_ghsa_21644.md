# [C] SQL injection in francoisjacquet/rosariosis

## Summary
Severity: Critical
Advisory: GHSA-82rr-mq4r-p4r3
CVE: CVE-2021-44567
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-82rr-mq4r-p4r3
Type: github-advisory

## Affected
- Packagist: `francoisjacquet/rosariosis` — affected >=0 <7.6.1

## Details
An SQL Injection vulnerability exits in RosarioSIS before 7.6.1 via the votes parameter in ProgramFunctions/PortalPollsNotes.fnc.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44567
- https://gitlab.com/francoisjacquet/rosariosis
- https://gitlab.com/francoisjacquet/rosariosis/-/blob/mobile/CHANGES.md#changes-in-761
- https://gitlab.com/francoisjacquet/rosariosis/-/commit/519af055a4fdc1362657d75bca76f9c95a081eaa
- https://gitlab.com/francoisjacquet/rosariosis/-/commit/e001430aa9fb53d2502fb6f036f6c51c578d2016
- https://gitlab.com/francoisjacquet/rosariosis/-/issues/308
