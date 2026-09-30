# [C] Apache ActiveMQ NMS OpenWire Client: deserialization allowlist bypass

## Summary
Severity: Critical
Advisory: CVE-2025-29953
Aliases: GHSA-9g64-r942-fvmp
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-29953
Type: osv

## Details
Deserialization of Untrusted Data vulnerability in Apache ActiveMQ NMS OpenWire Client.

This issue affects Apache ActiveMQ NMS OpenWire Client before 2.1.1 when performing connections to untrusted servers. Such servers could abuse the unbounded deserialization in the client to provide malicious responses that may eventually cause arbitrary code execution on the client. Version 2.1.0 introduced a allow/denylist feature to restrict deserialization, but this feature could be bypassed.

The .NET team has deprecated the built-in .NET binary serialization feature starting with .NET 9 and suggests migrating away from binary serialization. The project is considering to follow suit and drop this part of the NMS API altogether.

Users are recommended to upgrade to version 2.1.1, which fixes the issue. We also recommend to migrate away from relying on .NET binary serialization as a hardening method for the future.

## References
- http://www.openwall.com/lists/oss-security/2025/04/18/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29953.json
- https://lists.apache.org/thread/vc1sj9y3056d3kkhcvrs9fyw5w8kpmlx
- https://nvd.nist.gov/vuln/detail/CVE-2025-29953
