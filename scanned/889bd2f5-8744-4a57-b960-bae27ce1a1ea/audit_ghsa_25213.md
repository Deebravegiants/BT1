# [M] Apache Ambari reveals administrator passwords

## Summary
Severity: Medium
Advisory: GHSA-q3pw-6vf2-66hf
CVE: CVE-2016-4976
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q3pw-6vf2-66hf
Type: github-advisory

## Affected
- Maven: `org.apache.ambari:ambari` — affected >=2.0.0 <2.4.0

## Details
Apache Ambari 2.x before 2.4.0 includes KDC administrator passwords on the kadmin command line, which allows local users to obtain sensitive information via a process listing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4976
- https://cwiki.apache.org/confluence/display/AMBARI/Ambari+Vulnerabilities#AmbariVulnerabilities-FixedinAmbari2.4.0
- https://github.com/apache/ambari
- https://web.archive.org/web/20210124014838/http://www.securityfocus.com/bid/97229
