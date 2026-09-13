# [H] Spark allows remote attackers to read arbitrary files via a .. (dot dot) in the URI

## Summary
Severity: High
Advisory: GHSA-89gc-6cw6-4vch
CVE: CVE-2016-9177
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-04
Source: https://github.com/advisories/GHSA-89gc-6cw6-4vch
Type: github-advisory

## Affected
- Maven: `com.sparkjava:spark-core` — affected >=0 <2.5.2

## Details
Directory traversal vulnerability in Spark 2.5 allows remote attackers to read arbitrary files via a .. (dot dot) in the URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9177
- https://github.com/perwendel/spark/issues/700
- https://access.redhat.com/errata/RHSA-2017:0868
- https://github.com/advisories/GHSA-89gc-6cw6-4vch
- https://github.com/perwendel/spark
- http://seclists.org/fulldisclosure/2016/Nov/13
- http://www.securityfocus.com/bid/94218
