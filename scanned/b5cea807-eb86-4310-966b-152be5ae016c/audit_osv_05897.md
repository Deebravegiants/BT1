# [M] BIT-java-2023-22067

## Summary
Severity: Medium
Advisory: BIT-java-2023-22067
Aliases: BIT-java-min-2023-22067, BIT-jre-2023-22067, CVE-2023-22067
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-22067
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.391

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: CORBA).  Supported versions that are affected are Oracle Java SE: 8u381, 8u381-perf; Oracle GraalVM Enterprise Edition: 20.3.11 and  21.3.7. Easily exploitable vulnerability allows unauthenticated attacker with network access via CORBA to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized update, insert or delete access to some of Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability can only be exploited by supplying data to APIs in the specified Component without using Untrusted Java Web Start applications or Untrusted Java applets, such as through a web service. CVSS 3.1 Base Score 5.3 (Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22067
- https://openjdk.org/groups/vulnerability/advisories/2023-10-17
- https://security.netapp.com/advisory/ntap-20231027-0006/
- https://security.netapp.com/advisory/ntap-20241108-0002/
- https://www.debian.org/security/2023/dsa-5537
- https://www.oracle.com/security-alerts/cpuoct2023.html
