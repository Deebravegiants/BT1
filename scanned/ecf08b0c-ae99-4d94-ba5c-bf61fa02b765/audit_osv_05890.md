# [M] BIT-java-2023-21835

## Summary
Severity: Medium
Advisory: BIT-java-2023-21835
Aliases: BIT-java-min-2023-21835, BIT-jre-2023-21835, CVE-2023-21835
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-21835
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <19.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: JSSE).  Supported versions that are affected are Oracle Java SE: 11.0.17, 17.0.5, 19.0.1; Oracle GraalVM Enterprise Edition: 20.3.8, 21.3.4 and  22.3.0. Easily exploitable vulnerability allows unauthenticated attacker with network access via DTLS to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in unauthorized ability to cause a partial denial of service (partial DOS) of Oracle Java SE, Oracle GraalVM Enterprise Edition. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 5.3 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-21835
- https://openjdk.org/groups/vulnerability/advisories/2023-01-17
- https://security.gentoo.org/glsa/202401-25
- https://www.oracle.com/security-alerts/cpujan2023.html
