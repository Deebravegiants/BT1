# [M] BIT-java-2022-21426

## Summary
Severity: Medium
Advisory: BIT-java-2022-21426
Aliases: BIT-java-min-2022-21426, BIT-jre-2022-21426, CVE-2022-21426
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2022-21426
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <18.0.1

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: JAXP). Supported versions that are affected are Oracle Java SE: 7u331, 8u321, 11.0.14, 17.0.2, 18; Oracle GraalVM Enterprise Edition: 20.3.5, 21.3.1 and 22.0.0.2. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized ability to cause a partial denial of service (partial DOS) of Oracle Java SE, Oracle GraalVM Enterprise Edition. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L).

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00017.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-21426
- https://security.netapp.com/advisory/ntap-20220429-0006/
- https://www.debian.org/security/2022/dsa-5128
- https://www.debian.org/security/2022/dsa-5131
- https://www.oracle.com/security-alerts/cpuapr2022.html
