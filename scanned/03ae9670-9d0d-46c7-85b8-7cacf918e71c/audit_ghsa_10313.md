# [M] Apache DolphinScheduler RPC module has a Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f786-9c63-8xr8
CVE: CVE-2025-62233
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-f786-9c63-8xr8
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=3.2.0 <3.3.1
- Maven: `org.apache.dolphinscheduler:dolphinscheduler-rpc` — affected >=3.2.0 <3.3.1

## Details
Deserialization of Untrusted Data vulnerability in Apache DolphinScheduler RPC module.

This issue affects Apache DolphinScheduler: 

Version >= 3.2.0 and < 3.3.1.

Attackers who can access the Master or Worker nodes can compromise the system by creating a StandardRpcRequest, injecting a malicious class type into it, and sending RPC requests to the DolphinScheduler Master/Worker nodes.
Users are recommended to upgrade to version [3.3.1], which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62233
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/79s80h51r4z5d4l2xs5xy364rmmo1bw0
- http://www.openwall.com/lists/oss-security/2026/04/24/2
