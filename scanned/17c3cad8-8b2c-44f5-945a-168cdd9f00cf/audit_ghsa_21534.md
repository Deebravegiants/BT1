# [M] Apache DolphinScheduler vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-fp35-xrrr-3gph
CVE: CVE-2022-34662
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-fp35-xrrr-3gph
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=0 <3.0.0

## Details
When users add resources to the resource center with a relation path, this vulnerability will cause path traversal issues for logged-in users. Users should upgrade to version 3.0.0 to avoid this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34662
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/pbdzqf9ntxyvs4cr0x2dgk9zlf43btz8
- http://www.openwall.com/lists/oss-security/2022/11/01/13
