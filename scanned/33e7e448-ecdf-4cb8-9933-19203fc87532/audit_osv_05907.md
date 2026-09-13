# [M] BIT-java-2024-20926

## Summary
Severity: Medium
Advisory: BIT-java-2024-20926
Aliases: BIT-java-min-2024-20926, BIT-jre-2024-20926, CVE-2024-20926
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-20926
Type: osv

## Affected
- Bitnami: `java` — affected >=9.0.0 <11.0.22

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Scripting).  Supported versions that are affected are Oracle Java SE: 8u391, 8u391-perf, 11.0.21; Oracle GraalVM for JDK: 17.0.9; Oracle GraalVM Enterprise Edition: 20.3.12, 21.3.8 and  22.3.4. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 5.9 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00023.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-20926
- https://openjdk.org/groups/vulnerability/advisories/2024-01-16
- https://security.netapp.com/advisory/ntap-20240201-0002/
- https://security.netapp.com/advisory/ntap-20241108-0002/
- https://www.oracle.com/security-alerts/cpujan2024.html
