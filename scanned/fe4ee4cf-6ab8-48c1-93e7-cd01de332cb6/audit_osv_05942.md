# [H] BIT-java-2025-50059

## Summary
Severity: High
Advisory: BIT-java-2025-50059
Aliases: BIT-java-min-2025-50059, BIT-jre-2025-50059, CVE-2025-50059
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-50059
Type: osv

## Affected
- Bitnami: `java` — affected >=22.0.0 <24.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Networking).  Supported versions that are affected are Oracle Java SE: 8u451-perf, 11.0.27, 17.0.15, 21.0.7, 24.0.1; Oracle GraalVM for JDK: 17.0.15, 21.0.7 and  24.0.1; Oracle GraalVM Enterprise Edition: 21.3.14. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  While the vulnerability is in Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition, attacks may significantly impact additional products (scope change).  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 8.6 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00011.html
- https://lists.debian.org/debian-lts-announce/2025/08/msg00014.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-50059
- https://www.oracle.com/security-alerts/cpujul2025.html
