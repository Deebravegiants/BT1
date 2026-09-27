# [H] Apache James vulnerable to denial of service through JMAP HTML to text conversion

## Summary
Severity: High
Advisory: GHSA-57m2-h3fw-rxhw
CVE: CVE-2024-45626
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-57m2-h3fw-rxhw
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server-jmap-draft` — affected >=3.8.0 <3.8.2
- Maven: `org.apache.james:james-server-jmap-draft` — affected >=0 <3.7.6

## Details
Apache James server JMAP HTML to text plain implementation in versions below 3.8.2 and 3.7.6 is subject to unbounded memory consumption that can result in a denial of service.

Users are recommended to upgrade to version 3.7.6 and 3.8.2, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45626
- https://github.com/apache/james-project/pull/1422
- https://github.com/apache/james-project/commit/372f1f83b6825fb0f92147803a9bf215b8ff690d
- https://github.com/apache/james-project/commit/537ae380f9837f74c075f0ed2b625affa9b20122
- https://github.com/linagora/james-project
- https://lists.apache.org/thread/1fr9hvpsylomwwfr3rv82g84sxszn4kl
- http://www.openwall.com/lists/oss-security/2025/02/05/7
