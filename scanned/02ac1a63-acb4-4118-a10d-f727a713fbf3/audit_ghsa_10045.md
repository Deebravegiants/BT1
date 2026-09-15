# [H] Apache OpenMeetings Uses GET Request Method With Sensitive Query Strings 

## Summary
Severity: High
Advisory: GHSA-gcvm-c75m-h4p4
CVE: CVE-2026-34020
CWE: CWE-598
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-gcvm-c75m-h4p4
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=3.1.3 <9.0.0

## Details
Use of GET Request Method With Sensitive Query Strings vulnerability in Apache OpenMeetings.

The REST login endpoint uses HTTP GET method with username and password passed as query parameters. Please check references regarding possible impact


This issue affects Apache OpenMeetings: from 3.1.3 before 9.0.0.

Users are recommended to upgrade to version 9.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34020
- https://github.com/apache/openmeetings
- https://lists.apache.org/thread/2h3h9do5tp17xldr0nps1yjmkx4vs3db
- https://owasp.org/www-community/vulnerabilities/Information_exposure_through_query_strings_in_url
- http://www.openwall.com/lists/oss-security/2026/04/09/12
