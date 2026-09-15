# [H] Apache ZooKeeper: Authentication bypass with IP-based authentication in Admin Server

## Summary
Severity: High
Advisory: GHSA-g93m-8x6h-g5gv
CVE: CVE-2024-51504
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-g93m-8x6h-g5gv
Type: github-advisory

## Affected
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.9.0 <3.9.3

## Details
When using IPAuthenticationProvider in ZooKeeper Admin Server there is a possibility of Authentication Bypass by Spoofing -- this only impacts IP based authentication implemented in ZooKeeper Admin Server. Default configuration of client's IP address detection in IPAuthenticationProvider, which uses HTTP request headers, is weak and allows an attacker to bypass authentication via spoofing client's IP address in request headers. Default configuration honors X-Forwarded-For HTTP header to read client's IP address. X-Forwarded-For request header is mainly used by proxy servers to identify the client and can be easily spoofed by an attacker pretending that the request comes from a different IP address. Admin Server commands, such as snapshot and restore arbitrarily can be executed on successful exploitation which could potentially lead to information leakage or service availability issues. Users are recommended to upgrade to version 3.9.3, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51504
- https://github.com/apache/zookeeper/commit/2c2b74c1c11b6531aabb1bf06782e859048d5983
- https://github.com/apache/zookeeper
- https://lists.apache.org/thread/b3qrmpkto5r6989qr61fw9y2x646kqlh
- http://www.openwall.com/lists/oss-security/2024/11/06/5
