# [M] BIT-java-2024-21235

## Summary
Severity: Medium
Advisory: BIT-java-2024-21235
Aliases: BIT-java-min-2024-21235, BIT-jre-2024-21235, CVE-2024-21235
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-21235
Type: osv

## Affected
- Bitnami: `java` — affected >=22.0.0 <23.0.1

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Hotspot).  Supported versions that are affected are Oracle Java SE: 8u421, 8u421-perf, 11.0.24, 17.0.12, 21.0.4, 23;   Oracle GraalVM for JDK: 17.0.12, 21.0.4, 23;   Oracle GraalVM Enterprise Edition: 20.3.15 and  21.3.11. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized update, insert or delete access to some of Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data as well as  unauthorized read access to a subset of Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 4.8 (Confidentiality and Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00018.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00020.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-21235
- https://openjdk.org/groups/vulnerability/advisories/2024-10-15
- https://www.oracle.com/security-alerts/cpuoct2024.html
