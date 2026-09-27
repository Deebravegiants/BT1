# [M] Improper Privilege Management in Apache Sling

## Summary
Severity: Medium
Advisory: GHSA-mrpv-5pmr-p92h
CVE: CVE-2023-25621
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-mrpv-5pmr-p92h
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.i18n` — affected >=0 <2.6.2

## Details
Privilege Escalation vulnerability in Apache Software Foundation Apache Sling. Any content author is able to create i18n dictionaries in the repository in a location the author has write access to. As these translations are used across the whole product, it allows an author to change any text or dialog in the product. For example an attacker might fool someone by changing the text on a delete button to "Info". This issue affects the i18n module of Apache Sling versions before 2.6.2. Version 2.6.2 and higher limit by default i18m dictionaries to certain paths in the repository (/libs and /apps). Users of the module are advised to update to version 2.6.2 or higher, check the configuration for resource loading and then adjust the access permissions for the configured path accordingly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25621
- https://github.com/apache/sling-org-apache-sling-i18n/pull/9
- https://issues.apache.org/jira/browse/SLING-11744
- https://seclists.org/oss-sec/2023/q1/112
- https://sling.apache.org/news.html
