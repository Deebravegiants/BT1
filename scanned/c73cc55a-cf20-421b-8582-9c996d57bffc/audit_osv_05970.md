# [M] BIT-java-2026-47013

## Summary
Severity: Medium
Advisory: BIT-java-2026-47013
Aliases: BIT-java-min-2026-47013, BIT-jre-2026-47013, CVE-2026-47013
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-java-2026-47013
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.501

## Details
Vulnerability in Oracle Java SE (component: JavaFX). The supported version that is affected is Oracle Java SE: 8u491. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE. Successful attacks of this vulnerability can result in unauthorized ability to cause a partial denial of service (partial DOS) of Oracle Java SE. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47013
- https://openjdk.org/groups/vulnerability/advisories/2026-07-21
- https://www.oracle.com/security-alerts/cpujul2026.html
