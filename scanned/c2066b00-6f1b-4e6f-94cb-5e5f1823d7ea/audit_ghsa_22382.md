# [M] Trac has vulnerability in HTML sanitizer filter

## Summary
Severity: Medium
Advisory: GHSA-ww53-wxxr-8f9w
CVE: CVE-2008-5647
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-ww53-wxxr-8f9w
Type: github-advisory

## Affected
- PyPI: `Trac` — affected >=0 <0.11.2

## Details
Unspecified vulnerability in the HTML sanitizer filter in Trac before 0.11.2 allows attackers to conduct phishing attacks via unknown attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-5647
- https://exchange.xforce.ibmcloud.com/vulnerabilities/46491
- https://github.com/pypa/advisory-database/tree/main/vulns/trac/PYSEC-2008-7.yaml
- https://web.archive.org/web/20140722200717/http://secunia.com/advisories/32652
- https://web.archive.org/web/20200228023138/http://www.securityfocus.com/bid/32226
- http://trac.edgewall.org/wiki/ChangeLog
