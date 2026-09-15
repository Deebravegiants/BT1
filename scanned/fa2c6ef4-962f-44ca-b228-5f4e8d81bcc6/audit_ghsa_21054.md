# [M] Apache Druid before 0.23.0 vulnerable to clickjacking

## Summary
Severity: Medium
Advisory: GHSA-pgq7-jcj5-xx6h
CVE: CVE-2022-28889
CWE: CWE-1021
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-08
Source: https://github.com/advisories/GHSA-pgq7-jcj5-xx6h
Type: github-advisory

## Affected
- Maven: `org.apache.druid:druid` — affected >=0 <0.23.0

## Details
In Apache Druid 0.22.1 and earlier, the server did not set appropriate headers to prevent clickjacking. Druid 0.23.0 and later prevent clickjacking using the Content-Security-Policy header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28889
- https://github.com/apache/druid
- https://lists.apache.org/thread/t3nsq4crdr8wqgmj721d2wg6pf26s5cw
