# [M] Open Redirect in Apache Superset

## Summary
Severity: Medium
Advisory: GHSA-pfwg-rxf4-97c3
CVE: CVE-2021-28125
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-pfwg-rxf4-97c3
Type: github-advisory

## Affected
- PyPI: `superset` — affected >=0
- PyPI: `apache-superset` — affected >=0 <1.1.0

## Details
Apache Superset prior to 1.1.0 allowed for the creation of an external URL that could be malicious. By not checking user input for open redirects the URL shortener functionality would allow for a malicious user to create a short URL for a dashboard that could convince the user to click the link.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28125
- https://github.com/apache/superset/commit/eb35b804acf4d84cb70d02743e04b8afebbee029
- https://github.com/advisories/GHSA-pfwg-rxf4-97c3
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2021-128.yaml
- https://lists.apache.org/thread.html/r89b5d0dd35c1adc9624b48d6247729c73b2641b32754226661368434%40%3Cdev.superset.apache.org%3E
- https://lists.apache.org/thread.html/r89b5d0dd35c1adc9624b48d6247729c73b2641b32754226661368434@%3Cdev.superset.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/04/27/2
