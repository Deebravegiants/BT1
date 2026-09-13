# [C] PySAML2 XML external entity attack

## Summary
Severity: Critical
Advisory: GHSA-m269-wj6g-c459
CVE: CVE-2016-10127
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m269-wj6g-c459
Type: github-advisory

## Affected
- PyPI: `pysaml2` — affected >=0 <4.5.0

## Details
PySAML2 allows remote attackers to conduct XML external entity (XXE) attacks via a crafted SAML XML request or response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10127
- https://github.com/rohe/pysaml2/issues/366
- https://github.com/rohe/pysaml2/pull/379
- https://github.com/rohe/pysaml2/commit/6e09a25d9b4b7aa7a506853210a9a14100b8bc9b
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=850716
- https://github.com/advisories/GHSA-m269-wj6g-c459
- https://github.com/pypa/advisory-database/tree/main/vulns/pysaml2/PYSEC-2017-67.yaml
- https://github.com/rohe/pysaml2
- https://web.archive.org/web/20200227195127/http://www.securityfocus.com/bid/95376
- http://www.openwall.com/lists/oss-security/2017/01/19/5
