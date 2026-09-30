# [M] BIT-java-2023-22041

## Summary
Severity: Medium
Advisory: BIT-java-2023-22041
Aliases: BIT-java-min-2023-22041, BIT-jre-2023-22041, CVE-2023-22041
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-22041
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <20.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition, Oracle GraalVM for JDK product of Oracle Java SE (component: Hotspot).  Supported versions that are affected are Oracle Java SE: 8u371-perf, 11.0.19, 17.0.7, 20.0.1; Oracle GraalVM Enterprise Edition: 20.3.10, 21.3.6, 22.3.2; Oracle GraalVM for JDK: 17.0.7 and  20.0.1. Difficult to exploit vulnerability allows unauthenticated attacker with logon to the infrastructure where Oracle Java SE, Oracle GraalVM Enterprise Edition, Oracle GraalVM for JDK executes to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition, Oracle GraalVM for JDK.  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all Oracle Java SE, Oracle GraalVM Enterprise Edition, Oracle GraalVM for JDK accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 5.1 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00018.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-22041
- https://openjdk.org/groups/vulnerability/advisories/2023-07-18
- https://security.netapp.com/advisory/ntap-20230725-0006/
- https://www.debian.org/security/2023/dsa-5458
- https://www.debian.org/security/2023/dsa-5478
- https://www.oracle.com/security-alerts/cpujul2023.html
