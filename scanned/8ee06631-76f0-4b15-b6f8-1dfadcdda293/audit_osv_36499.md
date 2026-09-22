# [H] Apache Kyuubi: Unrestricted access via Kyuubi engine-ui proxy

## Summary
Severity: High
Advisory: CVE-2026-23904
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-23904
Type: osv

## Details
Kyuubi Engine UI proxy accepts a host and port from the request path and proxies HTTP requests to that destination. A remote requester with network access to the proxy can cause the Kyuubi server to send HTTP requests to arbitrary reachable hosts, resulting in SSRF or open-proxy behavior.


This issue affects Apache Kyuubi: from 1.8.0 before 1.12.0.

Users are recommended to upgrade to version 1.12.0, which disables the proxy by default. To restore proxied Engine UI, set kyuubi.frontend.rest.engine.ui.proxy.enabled=true and configure allowed target hosts with kyuubi.frontend.rest.engine.ui.proxy.hosts.

## References
- http://www.openwall.com/lists/oss-security/2026/07/29/3
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23904.json
- https://lists.apache.org/thread/ps79fcfx49ox9kwgztc5t5bw0tyhck9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-23904
- https://github.com/apache/kyuubi/pull/7483
