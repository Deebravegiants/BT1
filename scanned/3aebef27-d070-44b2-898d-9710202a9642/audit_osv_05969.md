# [M] BIT-java-2026-46968

## Summary
Severity: Medium
Advisory: BIT-java-2026-46968
Aliases: BIT-java-min-2026-46968, BIT-jre-2026-46968, CVE-2026-46968
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-java-2026-46968
Type: osv

## Affected
- Bitnami: `java` — affected >=26.0.0 <26.0.2

## Details
Vulnerability in Oracle Java SE (component: JSSE). Supported versions that are affected are Oracle Java SE: 8u491, 8u491-perf, 11.0.31, 17.0.19, 21.0.11, 25.0.3, 26.0.1; Oracle GraalVM for JDK: 17.0.19 and 21.0.11; Oracle GraalVM Enterprise Edition: 21.3.18. Difficult to exploit vulnerability allows unauthenticated attacker with network access via TLS to compromise Oracle Java SE. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all Oracle Java SE accessible data. Note: This vulnerability can only be exploited by supplying data to APIs in the specified Component without using Untrusted Java Web Start applications or Untrusted Java applets, such as through a web service. CVSS 3.1 Base Score 5.9 (Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46968
- https://openjdk.org/groups/vulnerability/advisories/2026-07-21
- https://www.oracle.com/security-alerts/cpujul2026.html
