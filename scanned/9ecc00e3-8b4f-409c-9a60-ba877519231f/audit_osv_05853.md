# [M] BIT-java-2021-35550

## Summary
Severity: Medium
Advisory: BIT-java-2021-35550
Aliases: BIT-java-min-2021-35550, BIT-jre-2021-35550, CVE-2021-35550
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2021-35550
Type: osv

## Affected
- Bitnami: `java` — affected >=9.0.0 <11.0.13

## Details
Vulnerability in the Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: JSSE). Supported versions that are affected are Java SE: 7u311, 8u301, 11.0.12; Oracle GraalVM Enterprise Edition: 20.3.3 and 21.2.0. Difficult to exploit vulnerability allows unauthenticated attacker with network access via TLS to compromise Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized access to critical data or complete access to all Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 5.9 (Confidentiality impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6EUURAQOIJYFZHQ7DFZCO6IKDPIAWTNK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7WTVCIVHTX3XONYOEGUMLKCM4QEC6INT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DJILEHYV2U37HKMGFEQ7CAVOV4DUWW2O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GTYZWIXDFUV2H57YQZJWPOD3BC3I3EIQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GXTUWAWXVU37GRNIG4TPMA47THO6VAE6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V362B2BWTH5IJDL45QPQGMBKIQOG7JX5/
- https://nvd.nist.gov/vuln/detail/CVE-2021-35550
- https://security.gentoo.org/glsa/202209-05
- https://security.netapp.com/advisory/ntap-20211022-0004/
- https://security.netapp.com/advisory/ntap-20240621-0006/
- https://www.debian.org/security/2021/dsa-5000
- https://www.oracle.com/security-alerts/cpuoct2021.html
