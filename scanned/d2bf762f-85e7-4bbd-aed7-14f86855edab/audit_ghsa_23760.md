# [M] Cross-site Scripting in Apache Jetspeed

## Summary
Severity: Medium
Advisory: GHSA-hj2v-85ph-8g48
CVE: CVE-2016-0712
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hj2v-85ph-8g48
Type: github-advisory

## Affected
- Maven: `org.apache.portals.jetspeed-2:jetspeed` — affected >=0 <2.3.1

## Details
Cross-site scripting (XSS) vulnerability in Apache Jetspeed before 2.3.1 allows remote attackers to inject arbitrary web script or HTML via the PATH_INFO to portal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0712
- https://mail-archives.apache.org/mod_mbox/portals-jetspeed-user/201603.mbox/%3CF868DBFC-A05C-4ABB-8B91-17CA54C174B9@bluesunrise.com%3E
- https://portals.apache.org/jetspeed-2/security-reports.html#CVE-2016-0712
