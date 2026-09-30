# [H] Logic error in Apache Pinot

## Summary
Severity: High
Advisory: GHSA-29f8-q7mf-7cqj
CVE: CVE-2022-23974
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-29f8-q7mf-7cqj
Type: github-advisory

## Affected
- Maven: `org.apache.pinot:pinot` — affected >=0 <0.10.0

## Details
In 0.9.3 or older versions of Apache Pinot segment upload path allowed segment directories to be imported into pinot tables. In pinot installations that allow open access to the controller a specially crafted request can potentially be exploited to cause disruption in pinot service. Pinot release 0.10.0 fixes this. See https://docs.pinot.apache.org/basics/releases/0.10.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23974
- https://github.com/apache/pinot/pull/7969
- https://docs.pinot.apache.org/basics/releases/0.10.0
- https://github.com/apache/pinot
- https://lists.apache.org/thread/3dk8pf1n02p8oj2j3czbtchyjsf8khwr
