# [M] BIT-java-2024-20919

## Summary
Severity: Medium
Advisory: BIT-java-2024-20919
Aliases: BIT-java-min-2024-20919, BIT-jre-2024-20919, CVE-2024-20919
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-20919
Type: osv

## Affected
- Bitnami: `java` — affected >=18.0.0 <21.0.2

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Hotspot).  Supported versions that are affected are Oracle Java SE: 8u391, 8u391-perf, 11.0.21, 17.0.9, 21.0.1; Oracle GraalVM for JDK: 17.0.9, 21.0.1; Oracle GraalVM Enterprise Edition: 20.3.12, 21.3.8 and  22.3.4. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized creation, deletion or modification access to critical data or all Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability can only be exploited by supplying data to APIs in the specified Component without using Untrusted Java Web Start applications or Untrusted Java applets, such as through a web service. CVSS 3.1 Base Score 5.9 (Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-20919
- https://openjdk.org/groups/vulnerability/advisories/2024-01-16
- https://security.netapp.com/advisory/ntap-20240201-0002/
- https://security.netapp.com/advisory/ntap-20241108-0002/
- https://www.oracle.com/security-alerts/cpujan2024.html
