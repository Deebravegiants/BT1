# [M] BIT-java-2022-21541

## Summary
Severity: Medium
Advisory: BIT-java-2022-21541
Aliases: BIT-java-min-2022-21541, BIT-jre-2022-21541, CVE-2022-21541
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2022-21541
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <18.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Hotspot). Supported versions that are affected are Oracle Java SE: 7u343, 8u333, 11.0.15.1, 17.0.3.1, 18.0.1.1; Oracle GraalVM Enterprise Edition: 20.3.6, 21.3.2 and 22.1.0. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 5.9 (Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H4YNJSJ64NPCNKFPNBYITNZU5H3L4D6L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I5OZNAZJ4YHLOKRRRZSWRT5OJ25E4XLM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JN3EVGR7FD3ZLV5SBTJXUIDCMSK4QUE2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KO3DXNKZ4EU3UZBT6AAR4XRKCD73KLMO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L3XPOTPPBZIPFBZHQE5E7OW6PDACUMCJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YULPNO3PAWMEQQZV2C54I3H3ZOXFZUTB/
- https://nvd.nist.gov/vuln/detail/CVE-2022-21541
- https://security.gentoo.org/glsa/202401-25
- https://security.netapp.com/advisory/ntap-20220729-0009/
- https://www.debian.org/security/2022/dsa-5188
- https://www.debian.org/security/2022/dsa-5192
- https://www.oracle.com/security-alerts/cpujul2022.html
