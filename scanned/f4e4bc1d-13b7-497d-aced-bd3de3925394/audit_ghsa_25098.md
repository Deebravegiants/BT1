# [H] Apache Wicket insecure defaults

## Summary
Severity: High
Advisory: GHSA-vfmm-jm4v-7frq
CVE: CVE-2014-7808
CWE: CWE-326
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vfmm-jm4v-7frq
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-core` — affected >=0 <1.5.13
- Maven: `org.apache.wicket:wicket-core` — affected >=6.0.0-beta1 <6.19.0
- Maven: `org.apache.wicket:wicket-core` — affected >=7.0.0-M1 <7.0.0-M5

## Details
Apache Wicket before 1.5.13, 6.x before 6.19.0, and 7.x before 7.0.0-M5 make it easier for attackers to defeat a cryptographic protection mechanism and predict encrypted URLs by leveraging use of CryptoMapper as the default encryption provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7808
- https://github.com/apache/wicket/commit/d2b8848346b8f806e747dca18799d70c37fc893f
- https://github.com/apache/wicket
- https://lists.apache.org/thread/rqy6lpo5mzco85cbf65r53vdh87gz77b
- https://web.archive.org/web/20180830051017/https://www.smrrd.de/cve-2014-7808-apache-wicket-csrf-2014.html
