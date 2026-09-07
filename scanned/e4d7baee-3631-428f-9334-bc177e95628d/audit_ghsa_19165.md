# [C] Apache EventMesh: raft Hessian Deserialization Vulnerability allowing remote code execution

## Summary
Severity: Critical
Advisory: GHSA-ffvr-gmp3-xx43
CVE: CVE-2024-56180
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-ffvr-gmp3-xx43
Type: github-advisory

## Affected
- Maven: `org.apache.eventmesh:eventmesh-meta-raft` — affected >=1.10.1 <1.11.0

## Details
CWE-502 Deserialization of Untrusted Data at the eventmesh-meta-raft plugin module in Apache EventMesh master branch without release version on windows\linux\mac os e.g. platforms allows attackers to send controlled message and remote code execute via hessian deserialization rpc protocol. Users can use the code under the master branch in project repo or version 1.11.0 to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56180
- https://github.com/apache/eventmesh
- https://lists.apache.org/thread/k9fw0t5r7t1vbx53gs8d1r8c54rhx0wd
- https://www.cve.org/CVERecord?id=CVE-2024-56180
- http://www.openwall.com/lists/oss-security/2025/02/14/7
