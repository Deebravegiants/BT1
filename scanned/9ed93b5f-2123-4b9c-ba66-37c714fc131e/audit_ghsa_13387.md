# [C] Apache StreamPark Path Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6874-289g-f7h7
CVE: CVE-2022-45802
CWE: CWE-22, CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-6874-289g-f7h7
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark-common_2.12` — affected >=0 <2.0.0
- Maven: `org.apache.streampark:streampark-common_2.11` — affected >=0 <2.0.0

## Details
Streampark allows any users to upload a jar as application, but there is no mandatory verification of the uploaded file type. This means users may upload some high-risk files, and may upload them to any directory. Users of the affected versions should upgrade to Apache StreamPark 2.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45802
- https://github.com/apache/incubator-streampark/commit/0c87c6d8cf39ef2c31c1dea1a7df23d76f5e1236
- https://github.com/apache/incubator-streampark
- https://lists.apache.org/thread/thwl1v2h6r3c21x1qwff08o57qzjnst6
