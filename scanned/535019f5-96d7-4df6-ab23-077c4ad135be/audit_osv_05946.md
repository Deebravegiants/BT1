# [H] BIT-java-2025-53066

## Summary
Severity: High
Advisory: BIT-java-2025-53066
Aliases: BIT-java-min-2025-53066, BIT-jre-2025-53066, CVE-2025-53066
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-53066
Type: osv

## Affected
- Bitnami: `java` — affected >=22.0.0 <25.0.1

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: JAXP).  Supported versions that are affected are Oracle Java SE: 8u461, 8u461-perf, 11.0.28, 17.0.16, 21.0.8, 25; Oracle GraalVM for JDK: 17.0.16 and  21.0.8; Oracle GraalVM Enterprise Edition: 21.3.15. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 7.5 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00026.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-53066
- https://www.oracle.com/security-alerts/cpuoct2025.html
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
