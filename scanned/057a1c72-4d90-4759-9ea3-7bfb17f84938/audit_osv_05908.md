# [H] BIT-java-2024-20932

## Summary
Severity: High
Advisory: BIT-java-2024-20932
Aliases: BIT-java-min-2024-20932, BIT-jre-2024-20932, CVE-2024-20932
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-20932
Type: osv

## Affected
- Bitnami: `java` — affected >=17.0.0 <17.0.10

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Security).  Supported versions that are affected are Oracle Java SE: 17.0.9; Oracle GraalVM for JDK: 17.0.9; Oracle GraalVM Enterprise Edition: 21.3.8 and  22.3.4. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized creation, deletion or modification access to critical data or all Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 7.5 (Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-20932
- https://openjdk.org/groups/vulnerability/advisories/2024-01-16
- https://security.netapp.com/advisory/ntap-20240201-0002/
- https://www.oracle.com/security-alerts/cpujan2024.html
