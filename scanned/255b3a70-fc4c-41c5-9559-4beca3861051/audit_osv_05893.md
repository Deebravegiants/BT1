# [M] BIT-java-2023-21954

## Summary
Severity: Medium
Advisory: BIT-java-2023-21954
Aliases: BIT-java-min-2023-21954, BIT-jre-2023-21954, CVE-2023-21954
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-21954
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <17.0.7

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Hotspot).  Supported versions that are affected are Oracle Java SE: 8u361, 8u361-perf, 11.0.18, 17.0.6; Oracle GraalVM Enterprise Edition: 20.3.9, 21.3.5 and  22.3.1. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all Oracle Java SE, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS 3.1 Base Score 5.9 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N).

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00018.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-21954
- https://openjdk.org/groups/vulnerability/advisories/2023-04-18
- https://security.netapp.com/advisory/ntap-20230427-0008/
- https://security.netapp.com/advisory/ntap-20240621-0006/
- https://www.couchbase.com/alerts/
- https://www.debian.org/security/2023/dsa-5430
- https://www.debian.org/security/2023/dsa-5478
- https://www.oracle.com/security-alerts/cpuapr2023.html
