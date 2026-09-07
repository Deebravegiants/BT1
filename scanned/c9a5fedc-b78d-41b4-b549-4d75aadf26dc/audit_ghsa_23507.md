# [M] Ajenti Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9crx-p357-5vw8
CVE: CVE-2014-2260
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9crx-p357-5vw8
Type: github-advisory

## Affected
- PyPI: `ajenti` — affected >=0 <1.2.15

## Details
Cross-site scripting (XSS) vulnerability in `plugins/main/content/js/ajenti.coffee` in Ajenti before 1.2.15 allows remote authenticated users to inject arbitrary web script or HTML via the command field in the Cron functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2260
- https://github.com/Eugeny/ajenti/issues/233
- https://github.com/ajenti/ajenti/issues/233
- https://github.com/Eugeny/ajenti/commit/3270fd1d78391bb847b4c9ce37cf921f485b1310
- https://github.com/ajenti/ajenti/commit/3270fd1d78391bb847b4c9ce37cf921f485b1310
- https://github.com/ajenti/ajenti
- https://github.com/pypa/advisory-database/tree/main/vulns/ajenti/PYSEC-2014-98.yaml
- https://web.archive.org/web/20200229062920/http://www.securityfocus.com/bid/64982
- http://packetstormsecurity.com/files/124804/Ajenti-1.2.13-Cross-Site-Scripting.html
