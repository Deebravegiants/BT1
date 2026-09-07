# [H] High severity vulnerability that affects org.dspace:dspace-xmlui

## Summary
Severity: High
Advisory: GHSA-4m9r-5gqp-7j82
CVE: CVE-2016-10726
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-4m9r-5gqp-7j82
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-xmlui` — affected >=4.0 <4.5
- Maven: `org.dspace:dspace-xmlui` — affected >=5.0 <5.5
- Maven: `org.dspace:dspace-xmlui` — affected >=0 <3.6

## Details
The XMLUI feature in DSpace before 3.6, 4.x before 4.5, and 5.x before 5.5 allows directory traversal via the themes/ path in an attack with two or more arbitrary characters and a colon before a pathname, as demonstrated by a themes/Reference/aa:etc/passwd URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10726
- https://github.com/DSpace/DSpace/releases/tag/dspace-5.5
- https://github.com/advisories/GHSA-4m9r-5gqp-7j82
- https://jira.duraspace.org/browse/DS-3094
- https://wiki.duraspace.org/display/DSDOC5x/Release+Notes
