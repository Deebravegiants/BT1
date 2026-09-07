# [M] Apache Drill vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-xp4g-5xj6-6vpr
CVE: CVE-2017-12630
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xp4g-5xj6-6vpr
Type: github-advisory

## Affected
- Maven: `org.apache.drill:drill-common` — affected >=0 <1.12.0

## Details
In Apache Drill 1.11.0 and earlier, when submitting form from Query page, users are able to pass arbitrary script or HTML which will take effect on Profile page afterwards. Example: after submitting special script that returns cookie information from Query page, malicious user may obtain this information from Profile page afterwards.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12630
- https://github.com/apache/drill
- https://lists.apache.org/thread.html/608658a55d09e16542db41121a0a972c97448214cdc04071fd4db923@%3Cdev.drill.apache.org%3E
