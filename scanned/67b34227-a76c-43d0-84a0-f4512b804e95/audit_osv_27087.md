# [M] Io.vertx/vertx-core: memory leak due to the use of netty fastthreadlocal data structures in vertx

## Summary
Severity: Medium
Advisory: CVE-2024-1023
Aliases: GHSA-5667-3wch-7q7w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2024-1023
Type: osv

## Details
A vulnerability in the Eclipse Vert.x toolkit results in a memory leak due to using Netty FastThreadLocal data structures. Specifically, when the Vert.x HTTP client establishes connections to different hosts, triggering the memory leak. The leak can be accelerated with intimate runtime knowledge, allowing an attacker to exploit this vulnerability. For instance, a server accepting arbitrary internet addresses could serve as an attack vector by connecting to these addresses, thereby accelerating the memory leak.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://catalog.redhat.com/software/containers/
- https://mvnrepository.com/artifact/io.vertx
- https://access.redhat.com/errata/RHSA-2024:1662
- https://access.redhat.com/errata/RHSA-2024:1706
- https://access.redhat.com/errata/RHSA-2024:2088
- https://access.redhat.com/errata/RHSA-2024:2833
- https://access.redhat.com/errata/RHSA-2024:3527
- https://access.redhat.com/errata/RHSA-2024:3989
- https://access.redhat.com/errata/RHSA-2024:4884
- https://access.redhat.com/security/cve/CVE-2024-1023
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1023.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1023
- https://bugzilla.redhat.com/show_bug.cgi?id=2260840
- https://github.com/eclipse-vertx/vert.x/issues/5078
- https://github.com/eclipse-vertx/vert.x/pull/5080
- https://github.com/eclipse-vertx/vert.x/pull/5082
