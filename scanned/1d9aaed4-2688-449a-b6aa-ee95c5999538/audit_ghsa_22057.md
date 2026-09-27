# [H] Apache Storm log viewer path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-cpp8-r8pr-wv4v
CVE: CVE-2014-0115
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cpp8-r8pr-wv4v
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm` — affected >=0

## Details
Directory traversal vulnerability in the log viewer in Apache Storm 0.9.0.1 allows remote attackers to read arbitrary files via a `..` (dot dot) in the file parameter to log.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0115
- https://issues.apache.org/jira/browse/STORM-269
- https://mail-archives.apache.org/mod_mbox/storm-dev/201404.mbox/%3CJIRA.12704141.1395964296891.201561.1398799995645@arcas%3E
