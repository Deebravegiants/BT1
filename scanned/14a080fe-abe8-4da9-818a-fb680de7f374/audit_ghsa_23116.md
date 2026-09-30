# [H] Apache OpenMeetings allows remote attackers to read arbitrary files by attempting to upload a file

## Summary
Severity: High
Advisory: GHSA-f6vf-465r-h42p
CVE: CVE-2016-2164
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f6vf-465r-h42p
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=0 <3.1.1

## Details
The (1) FileService.importFileByInternalUserId and (2) FileService.importFile SOAP API methods in Apache OpenMeetings before 3.1.1 improperly use the Java URL class without checking the specified protocol handler, which allows remote attackers to read arbitrary files by attempting to upload a file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2164
- https://github.com/apache/openmeetings
- https://www.apache.org/dist/openmeetings/3.1.1/CHANGELOG
- http://openmeetings.apache.org/security.html
- http://packetstormsecurity.com/files/136434/Apache-OpenMeetings-3.0.7-Arbitary-File-Read.html
