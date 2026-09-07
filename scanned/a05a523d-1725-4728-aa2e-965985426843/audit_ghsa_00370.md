# [M] ZipSlip in org.apache.storm:storm-core

## Summary
Severity: Medium
Advisory: GHSA-898j-5cc8-cmf5
CVE: CVE-2018-8008
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-898j-5cc8-cmf5
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-core` — affected >=1.1.0 <1.1.3
- Maven: `org.apache.storm:storm-core` — affected >=1.2.0 <1.2.2
- Maven: `org.apache.storm:storm-core` — affected >=0 <1.0.7

## Details
Apache Storm version 1.0.6 and earlier, 1.2.1 and earlier, and version 1.1.2 and earlier expose an arbitrary file write vulnerability, that can be achieved using a specially crafted zip archive (affects other archives as well, bzip2, tar, xz, war, cpio, 7z), that holds path traversal filenames. So when the filename gets concatenated to the target extraction directory, the final path ends up outside of the target folder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8008
- https://github.com/apache/storm/commit/0fc6b522487c061f89e8cdacf09f722d3f20589
- https://github.com/apache/storm/commit/efad4cca2d7d461f5f8c08a0d7b51fabeb82d0a
- https://github.com/apache/storm/commit/f61e5daf299d6c37c7ad65744d02556c94a16a4
- https://github.com/advisories/GHSA-898j-5cc8-cmf5
- https://issues.apache.org/jira/browse/STORM-3052
- https://lists.apache.org/thread.html/613b2fca8bcd0a3b12c0b763ea8f7cf62e422e9f79fce6cfa5b08a58@%3Cdev.storm.apache.org%3E
- http://www.securityfocus.com/bid/104418
