# [C] Net-SNMP snmptrapd crash

## Summary
Severity: Critical
Advisory: CVE-2025-68615
Aliases: GHSA-4389-rwqf-q9gq
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2025-68615
Type: osv

## Details
net-snmp is a SNMP application library, tools and daemon. Prior to versions 5.9.5 and 5.10.pre2, a specially crafted packet to an net-snmp snmptrapd daemon can cause a buffer overflow and the daemon to crash. This issue has been patched in versions 5.9.5 and 5.10.pre2.

## References
- http://www.openwall.com/lists/oss-security/2026/01/09/2
- https://lists.debian.org/debian-lts-announce/2026/01/msg00000.html
- https://www.vicarius.io/vsociety/posts/cve-2025-68615-detection-script-buffer-overflow-vulnerability-affecting-net-snmp
- https://www.vicarius.io/vsociety/posts/cve-2025-68615-mitigation-script-buffer-overflow-vulnerability-affecting-net-snmp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68615.json
- https://github.com/net-snmp/net-snmp/security/advisories/GHSA-4389-rwqf-q9gq
- https://nvd.nist.gov/vuln/detail/CVE-2025-68615
