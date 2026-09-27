# [M] Apache Wicket has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-3gmf-p6r4-q8m6
CVE: CVE-2026-43975
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-3gmf-p6r4-q8m6
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-core` — affected >=8.0.0-M1
- Maven: `org.apache.wicket:wicket-core` — affected >=9.0.0-M1
- Maven: `org.apache.wicket:wicket-core` — affected >=10.0.0-M1 <10.9.0

## Details
FolderUploadsFileManager in Apache Wicket does not validate or sanitize the uploadFieldId parameter or the clientFileName
 before constructing file paths, allowing an unauthenticated attacker to
 write arbitrary files outside the intended upload directory or read 
files from arbitrary locations on the server.

This issue affects Apache Wicket: from 8.0.0 through 8.17.0, from 9.0.0 through 9.22.0, from 10.0.0 through 10.8.0.

Users are recommended to upgrade to version 10.9.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43975
- https://github.com/apache/wicket/pull/1432
- https://github.com/apache/wicket/commit/72470983f689c61e6a6c0b7388ef955f23bb1e16
- https://github.com/apache/wicket
- https://lists.apache.org/thread/xp2jrdk6ppv1zcmxb4w1mk2lg1dw3hbr
- http://www.openwall.com/lists/oss-security/2026/05/06/4
