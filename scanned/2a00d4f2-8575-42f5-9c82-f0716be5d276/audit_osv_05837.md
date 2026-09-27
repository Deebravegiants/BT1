# [M] BIT-java-2020-2585

## Summary
Severity: Medium
Advisory: BIT-java-2020-2585
Aliases: BIT-java-min-2020-2585, BIT-jre-2020-2585, CVE-2020-2585
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-2585
Type: osv

## Affected
- Bitnami: `java` — affected >=8.0.0 <8.0.241

## Details
Vulnerability in the Java SE product of Oracle Java SE (component: JavaFX). The supported version that is affected is Java SE: 8u231. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all Java SE accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets (in Java SE 8), that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.0 Base Score 5.9 (Integrity impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2585
- https://security.gentoo.org/glsa/202006-22
- https://security.gentoo.org/glsa/202209-15
- https://security.netapp.com/advisory/ntap-20200122-0003/
- https://www.oracle.com/security-alerts/cpujan2020.html
