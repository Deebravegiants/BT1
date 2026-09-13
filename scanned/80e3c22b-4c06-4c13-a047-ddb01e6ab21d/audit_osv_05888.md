# [M] BIT-java-2022-21628

## Summary
Severity: Medium
Advisory: BIT-java-2022-21628
Aliases: BIT-java-min-2022-21628, BIT-jre-2022-21628, CVE-2022-21628
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2022-21628
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <19.0.1

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Lightweight HTTP Server). Supported versions that are affected are Oracle Java SE: 8u341, 8u345-perf, 11.0.16.1, 17.0.4.1, 19; Oracle GraalVM Enterprise Edition: 20.3.7, 21.3.3 and 22.2.0. Easily exploitable vulnerability allows unauthenticated attacker with network access via HTTP to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized ability to cause a partial denial of service (partial DOS) of Oracle Java SE, Oracle GraalVM Enterprise Edition. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/37QDWJBGEPP65X43NXQTXQ7KASLUHON6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3ARF4QF4N3X5GSFHXUBWARGLISGKJ33R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QLQ7OD33W6LT3HWI7VYDFFJLV75Y73K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EXSBV3W6EP6B7XJ63Z2FPVBH6HAPGJ5T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HNGMDNIHAA73BEX6XPA2IMXJSGOKKYE6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PB3CIGOFG7CENUVVE4FFZT2HI5FO77XU/
- https://nvd.nist.gov/vuln/detail/CVE-2022-21628
- https://security.gentoo.org/glsa/202401-25
- https://security.netapp.com/advisory/ntap-20221028-0012/
- https://www.oracle.com/security-alerts/cpuoct2022.html
