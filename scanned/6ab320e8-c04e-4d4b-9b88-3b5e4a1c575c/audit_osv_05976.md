# [M] BIT-java-2026-60147

## Summary
Severity: Medium
Advisory: BIT-java-2026-60147
Aliases: BIT-java-min-2026-60147, BIT-jre-2026-60147, CVE-2026-60147
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-java-2026-60147
Type: osv

## Affected
- Bitnami: `java` — affected >=26.0.0 <26.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Security). Supported versions that are affected are Oracle Java SE: 8u491, 8u491-perf, 11.0.31, 17.0.19, 21.0.11, 25.0.3, 26.0.1; Oracle GraalVM for JDK: 17.0.19 and 21.0.11; Oracle GraalVM Enterprise Edition: 21.3.18. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data as well as unauthorized read access to a subset of Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 6.5 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-60147
- https://openjdk.org/groups/vulnerability/advisories/2026-07-21
- https://www.oracle.com/security-alerts/cpujul2026.html
