# [H] BIT-java-2026-22016

## Summary
Severity: High
Advisory: BIT-java-2026-22016
Aliases: BIT-java-min-2026-22016, BIT-jre-2026-22016, CVE-2026-22016
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2026-22016
Type: osv

## Affected
- Bitnami: `java` — affected >=26.0.0 <26.0.1

## Details
Vulnerability in the Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: JAXP).  Supported versions that are affected are Oracle Java SE: 8u481, 8u481-b50, 8u481-perf, 11.0.30, 17.0.18, 21.0.10, 25.0.2, 26; Oracle GraalVM for JDK: 17.0.18 and  21.0.10; Oracle GraalVM Enterprise Edition: 21.3.17. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition.  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all Oracle Java SE, Oracle GraalVM for JDK, Oracle GraalVM Enterprise Edition accessible data. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 7.5 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22016
- https://www.oracle.com/security-alerts/cpuapr2026.html
- https://access.redhat.com/errata/RHSA-2026:11403
- https://access.redhat.com/errata/RHSA-2026:11655
- https://access.redhat.com/errata/RHSA-2026:11822
- https://access.redhat.com/errata/RHSA-2026:11829
- https://access.redhat.com/errata/RHSA-2026:11902
- https://access.redhat.com/errata/RHSA-2026:22139
- https://access.redhat.com/errata/RHSA-2026:22328
- https://access.redhat.com/errata/RHSA-2026:9254
- https://access.redhat.com/errata/RHSA-2026:9256
- https://access.redhat.com/errata/RHSA-2026:9682
- https://access.redhat.com/errata/RHSA-2026:9683
- https://access.redhat.com/errata/RHSA-2026:9684
- https://access.redhat.com/errata/RHSA-2026:9686
- https://access.redhat.com/errata/RHSA-2026:9687
- https://access.redhat.com/errata/RHSA-2026:9688
- https://access.redhat.com/errata/RHSA-2026:9689
- https://access.redhat.com/errata/RHSA-2026:9691
- https://access.redhat.com/errata/RHSA-2026:9693
