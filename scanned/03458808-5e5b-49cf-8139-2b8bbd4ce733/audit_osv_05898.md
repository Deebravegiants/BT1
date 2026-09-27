# [M] BIT-java-2023-22081

## Summary
Severity: Medium
Advisory: BIT-java-2023-22081
Aliases: BIT-java-min-2023-22081, BIT-jre-2023-22081, CVE-2023-22081
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-22081
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <21.0.1

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: JSSE).  Supported versions that are affected are Oracle Java SE: 8u381, 8u381-perf, 11.0.20, 17.0.8, 21; Oracle GraalVM for JDK: 17.0.8, 21; Oracle GraalVM Enterprise Edition: 20.3.11, 21.3.7 and  22.3.3. Easily exploitable vulnerability allows unauthenticated attacker with network access via HTTPS to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in unauthorized ability to cause a partial denial of service (partial DOS) of Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 5.3 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L).

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00041.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-22081
- https://openjdk.org/groups/vulnerability/advisories/2023-10-17
- https://security.netapp.com/advisory/ntap-20231027-0006/
- https://security.netapp.com/advisory/ntap-20241108-0002/
- https://www.debian.org/security/2023/dsa-5537
- https://www.debian.org/security/2023/dsa-5548
- https://www.oracle.com/security-alerts/cpuoct2023.html
