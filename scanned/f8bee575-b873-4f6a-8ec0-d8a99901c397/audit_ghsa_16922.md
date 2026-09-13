# [M] Eclipse Vert.x vulnerable to a memory leak in TCP servers

## Summary
Severity: Medium
Advisory: GHSA-9ph3-v2vh-3qx7
CVE: CVE-2024-1300
CWE: CWE-400, CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2024-04-02
Source: https://github.com/advisories/GHSA-9ph3-v2vh-3qx7
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-core` — affected >=4.3.4 <4.4.8
- Maven: `io.vertx:vertx-core` — affected >=4.5.0 <4.5.3

## Details
A vulnerability in the Eclipse Vert.x toolkit causes a memory leak in TCP servers configured with TLS and SNI support. When processing an unknown SNI server name assigned the default certificate instead of a mapped certificate, the SSL context is erroneously cached in the server name map, leading to memory exhaustion. This flaw allows attackers to send TLS client hello messages with fake server names, triggering a JVM out-of-memory error.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1300
- https://github.com/eclipse-vertx/vert.x/pull/5101
- https://github.com/eclipse-vertx/vert.x/pull/5100
- https://github.com/eclipse-vertx/vert.x/pull/5099
- https://github.com/eclipse-vertx/vert.x/commit/7ad34ea9d78f85e26b231ee3ec8d492d10046479
- https://github.com/eclipse-vertx/vert.x/commit/3d9235cadf44df39a70dc75bddfe0b8fcbd6a683
- https://vertx.io/docs/vertx-core/java/#_server_name_indication_sni.
- https://github.com/eclipse-vertx/vert.x
- https://bugzilla.redhat.com/show_bug.cgi?id=2263139
- https://access.redhat.com/security/cve/CVE-2024-1300
- https://access.redhat.com/errata/RHSA-2024:4884
- https://access.redhat.com/errata/RHSA-2024:3989
- https://access.redhat.com/errata/RHSA-2024:3527
- https://access.redhat.com/errata/RHSA-2024:2833
- https://access.redhat.com/errata/RHSA-2024:2088
- https://access.redhat.com/errata/RHSA-2024:1923
- https://access.redhat.com/errata/RHSA-2024:1706
- https://access.redhat.com/errata/RHSA-2024:1662
