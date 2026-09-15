# [H] CVE-2021-27738

## Summary
Severity: High
Advisory: CVE-2021-27738
Aliases: GHSA-wrx7-qgmj-mf2q
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-01-06
Source: https://osv.dev/vulnerability/CVE-2021-27738
Type: osv

## Details
All request mappings in `StreamingCoordinatorController.java` handling `/kylin/api/streaming_coordinator/*` REST API endpoints did not include any security checks, which allowed an unauthenticated user to issue arbitrary requests, such as assigning/unassigning of streaming cubes, creation/modification and deletion of replica sets, to the Kylin Coordinator. For endpoints accepting node details in HTTP message body, unauthenticated (but limited) server-side request forgery (SSRF) can be achieved. This issue affects Apache Kylin Apache Kylin 3 versions prior to 3.1.2.

## References
- http://www.openwall.com/lists/oss-security/2022/01/06/6
- https://lists.apache.org/thread/vkohh0to2vzwymyb2x13fszs3cs3vd70
