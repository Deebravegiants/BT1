# [H] Apache Pulsar WebSocket Proxy contains an Improper Authentication vulnerability

## Summary
Severity: High
Advisory: GHSA-83q5-whqp-r8jr
CVE: CVE-2023-37544
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-20
Source: https://github.com/advisories/GHSA-83q5-whqp-r8jr
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-websocket` — affected >=0 <2.10.5
- Maven: `org.apache.pulsar:pulsar-websocket` — affected >=2.11.0 <2.11.2
- Maven: `org.apache.pulsar:pulsar-websocket` — affected >=3.0.0 <3.0.1

## Details
Improper Authentication vulnerability in Apache Pulsar WebSocket Proxy allows an attacker to connect to the /pingpong endpoint without authentication.

This issue affects Apache Pulsar WebSocket Proxy: from 2.8.0 through 2.8.*, from 2.9.0 through 2.9.*, from 2.10.0 through 2.10.4, from 2.11.0 through 2.11.1, 3.0.0.

The known risks include a denial of service due to the WebSocket Proxy accepting any connections, and excessive data transfer due to misuse of the WebSocket ping/pong feature.

2.10 Pulsar WebSocket Proxy users should upgrade to at least 2.10.5.
2.11 Pulsar WebSocket Proxy users should upgrade to at least 2.11.2.
3.0 Pulsar WebSocket Proxy users should upgrade to at least 3.0.1.
3.1 Pulsar WebSocket Proxy users are unaffected.
Any users running the Pulsar WebSocket Proxy for 2.8, 2.9, and earlier should upgrade to one of the above patched versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37544
- https://github.com/apache/pulsar/commit/11ee36d0351644a006d2a8639bdcc714fb602358
- https://github.com/apache/pulsar/commit/894192fb6542e504be43034a3c33e90f9c6e528a
- https://github.com/apache/pulsar/commit/eac263e8f2a93d3b9f707b97c7bbcbc2a826569f
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/od0k9zts1toc9h9snbqq4pjpyx28mv4m
- http://www.openwall.com/lists/oss-security/2023/12/20/2
