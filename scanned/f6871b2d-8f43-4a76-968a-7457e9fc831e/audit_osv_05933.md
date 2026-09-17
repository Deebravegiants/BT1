# [M] BIT-java-2025-30691

## Summary
Severity: Medium
Advisory: BIT-java-2025-30691
Aliases: BIT-java-min-2025-30691, BIT-jre-2025-30691, CVE-2025-30691
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-30691
Type: osv

## Affected
- Bitnami: `java` — affected >=22.0.0 <24.0.1

## Details
Vulnerability in Oracle Java SE (component: Compiler).  Supported versions that are affected are Oracle Java SE: 21.0.6, 24; Oracle GraalVM for JDK: 21.0.6 and  24. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE.  Successful attacks of this vulnerability can result in  unauthorized update, insert or delete access to some of Oracle Java SE accessible data as well as  unauthorized read access to a subset of Oracle Java SE accessible data. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 4.8 (Confidentiality and Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00026.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-30691
- https://security.netapp.com/advisory/ntap-20250418-0004/
- https://www.oracle.com/security-alerts/cpuapr2025.html
