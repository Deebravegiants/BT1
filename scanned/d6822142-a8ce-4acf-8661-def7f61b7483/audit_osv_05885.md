# [M] BIT-java-2022-21549

## Summary
Severity: Medium
Advisory: BIT-java-2022-21549
Aliases: BIT-java-min-2022-21549, BIT-jre-2022-21549, CVE-2022-21549
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2022-21549
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <17.0.4

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Libraries). Supported versions that are affected are Oracle Java SE: 17.0.3.1; Oracle GraalVM Enterprise Edition: 21.3.2 and 22.1.0. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 5.3 (Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NQICCJXXAYMCCXOO24R4W7Q3RSKCYDMX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UKJCLA2GDNF4B7ZRKORQ2TIR56AHJ4VC/
- https://nvd.nist.gov/vuln/detail/CVE-2022-21549
- https://security.gentoo.org/glsa/202401-25
- https://security.netapp.com/advisory/ntap-20220729-0009/
- https://www.debian.org/security/2022/dsa-5192
- https://www.oracle.com/security-alerts/cpujul2022.html
