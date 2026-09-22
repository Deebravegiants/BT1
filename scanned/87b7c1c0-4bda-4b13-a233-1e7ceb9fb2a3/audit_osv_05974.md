# [H] BIT-java-2026-47058

## Summary
Severity: High
Advisory: BIT-java-2026-47058
Aliases: BIT-java-min-2026-47058, BIT-jre-2026-47058, CVE-2026-47058
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-java-2026-47058
Type: osv

## Affected
- Bitnami: `java` — affected >=9.0.0 <11.0.32

## Details
Vulnerability in Oracle Java SE (component: Scripting). Supported versions that are affected are Oracle Java SE: 8u491, 8u491-perf and 11.0.31. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all Oracle Java SE accessible data as well as unauthorized access to critical data or complete access to all Oracle Java SE accessible data. Note: This vulnerability can be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. This vulnerability also applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. CVSS 3.1 Base Score 7.4 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47058
- https://openjdk.org/groups/vulnerability/advisories/2026-07-21
- https://www.oracle.com/security-alerts/cpujul2026.html
