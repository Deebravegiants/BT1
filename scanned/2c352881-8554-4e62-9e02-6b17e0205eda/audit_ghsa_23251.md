# [M] Ajenti Cross-site Scripting Via Filename

## Summary
Severity: Medium
Advisory: GHSA-5pcv-m8w2-62m9
CVE: CVE-2018-18548
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5pcv-m8w2-62m9
Type: github-advisory

## Affected
- PyPI: `ajenti` — affected >=0

## Details
Ajenti through v1.2.23.13 has a Cross-site Scripting (XSS) vulnerability via a filename that is mishandled in File Manager.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18548
- https://github.com/ajenti/ajenti
- https://github.com/pypa/advisory-database/tree/main/vulns/ajenti/PYSEC-2018-107.yaml
- https://numanozdemir.com/ajenti-xss.txt
- https://www.exploit-db.com/exploits/45691
- http://packetstormsecurity.com/files/149898/AjentiCP-1.2.23.13-Cross-Site-Scripting.html
