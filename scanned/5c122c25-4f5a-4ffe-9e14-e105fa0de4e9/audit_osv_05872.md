# [M] BIT-java-2022-21305

## Summary
Severity: Medium
Advisory: BIT-java-2022-21305
Aliases: BIT-java-min-2022-21305, BIT-jre-2022-21305, CVE-2022-21305
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2022-21305
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <17.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Hotspot). Supported versions that are affected are Oracle Java SE: 7u321, 8u311, 11.0.13, 17.0.1; Oracle GraalVM Enterprise Edition: 20.3.4 and 21.3.0. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 5.3 (Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2022/02/msg00011.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-21305
- https://security.gentoo.org/glsa/202209-05
- https://security.netapp.com/advisory/ntap-20220121-0007/
- https://www.debian.org/security/2022/dsa-5057
- https://www.debian.org/security/2022/dsa-5058
- https://www.oracle.com/security-alerts/cpujan2022.html
