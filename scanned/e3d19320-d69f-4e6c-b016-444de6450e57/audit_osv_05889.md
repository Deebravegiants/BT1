# [M] BIT-java-2023-21830

## Summary
Severity: Medium
Advisory: BIT-java-2023-21830
Aliases: BIT-java-min-2023-21830, BIT-jre-2023-21830, CVE-2023-21830
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-21830
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.361

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Serialization).  Supported versions that are affected are Oracle Java SE: 8u351, 8u351-perf; Oracle GraalVM Enterprise Edition: 20.3.8 and  21.3.4. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized update, insert or delete access to some of Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 5.3 (Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-21830
- https://openjdk.org/groups/vulnerability/advisories/2023-01-17
- https://security.gentoo.org/glsa/202401-25
- https://www.oracle.com/security-alerts/cpujan2023.html
- https://www.oracle.com/security-alerts/cpujul2023.html
