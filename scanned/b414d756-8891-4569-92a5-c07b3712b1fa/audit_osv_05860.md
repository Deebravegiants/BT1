# [M] BIT-java-2021-35567

## Summary
Severity: Medium
Advisory: BIT-java-2021-35567
Aliases: BIT-java-min-2021-35567, BIT-jre-2021-35567, CVE-2021-35567
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2021-35567
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <17.0.1

## Details
Vulnerability in the Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Libraries). Supported versions that are affected are Java SE: 8u301, 11.0.12, 17; Oracle GraalVM Enterprise Edition: 20.3.3 and 21.2.0. Easily exploitable vulnerability allows low privileged attacker with network access via Kerberos to compromise Java SE, Oracle GraalVM Enterprise Edition. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in Java SE, Oracle GraalVM Enterprise Edition, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized access to critical data or complete access to all Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 6.8 (Confidentiality impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6EUURAQOIJYFZHQ7DFZCO6IKDPIAWTNK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GTYZWIXDFUV2H57YQZJWPOD3BC3I3EIQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GXTUWAWXVU37GRNIG4TPMA47THO6VAE6/
- https://nvd.nist.gov/vuln/detail/CVE-2021-35567
- https://security.gentoo.org/glsa/202209-05
- https://security.netapp.com/advisory/ntap-20211022-0004/
- https://www.debian.org/security/2021/dsa-5000
- https://www.debian.org/security/2021/dsa-5012
- https://www.oracle.com/security-alerts/cpuoct2021.html
