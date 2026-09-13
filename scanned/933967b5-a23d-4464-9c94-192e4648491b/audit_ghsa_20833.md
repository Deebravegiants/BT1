# [C] Apache Pinot has Groovy Function support enabled by default

## Summary
Severity: Critical
Advisory: GHSA-qj9p-jvmw-82rh
CVE: CVE-2022-26112
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-qj9p-jvmw-82rh
Type: github-advisory

## Affected
- Maven: `org.apache.pinot:pinot` — affected >=0 <0.11.0

## Details
Pinot allows you to run any function using Apache Groovy scripts. In versions prior to 0.10.0, Pinot query endpoint and realtime ingestion layer has a vulnerability in unprotected environments due to groovy function support being enabled by default. This issue has been fixed by making function support disabled by default, in version 0.11.0. A potential workaround is to disable groovy script support.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26112
- https://github.com/apache/pinot/pull/8711
- https://docs.pinot.apache.org/basics/releases/0.11.0
- https://github.com/apache/pinot
- https://lists.apache.org/thread/4pb0r12s2b68d78llk04yd8rh3qk5t9h
