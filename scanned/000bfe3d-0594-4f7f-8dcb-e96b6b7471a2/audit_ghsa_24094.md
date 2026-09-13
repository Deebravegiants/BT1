# [M] Apache OpenMeetings Directory Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8xq7-7hcx-8p8g
CVE: CVE-2016-0784
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8xq7-7hcx-8p8g
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-install` — affected >=1.9.0 <3.1.1

## Details
Directory traversal vulnerability in the Import/Export System Backups functionality in Apache OpenMeetings before 3.1.1 allows remote authenticated administrators to write to arbitrary files via a .. (dot dot) in a ZIP archive entry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0784
- https://github.com/apache/openmeetings/commit/fbab8891d96f3352c37f1be303d9c9a685aa6847
- https://github.com/apache/openmeetings
- https://web.archive.org/web/20160330085718/http://haxx.ml/post/141655340521/all-your-meetings-are-belong-to-us-remote-code
- https://web.archive.org/web/20160617190447/https://www.apache.org/dist/openmeetings/3.1.1/CHANGELOG
- https://web.archive.org/web/20201209041006/http://www.securityfocus.com/archive/1/537929/100/0/threaded
- https://web.archive.org/web/20201221104133/http://packetstormsecurity.com/files/136484/Apache-OpenMeetings-3.1.0-Path-Traversal.html
- https://www.exploit-db.com/exploits/39642
- http://openmeetings.apache.org/security.html
- http://www.openwall.com/lists/oss-security/2016/03/25/2
