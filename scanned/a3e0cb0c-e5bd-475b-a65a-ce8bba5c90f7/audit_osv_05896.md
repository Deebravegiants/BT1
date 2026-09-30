# [M] BIT-java-2023-22043

## Summary
Severity: Medium
Advisory: BIT-java-2023-22043
Aliases: BIT-java-min-2023-22043, BIT-jre-2023-22043, CVE-2023-22043
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2023-22043
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.381

## Details
Vulnerability in Oracle Java SE (component: JavaFX).   The supported version that is affected is Oracle Java SE: 8u371. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Oracle Java SE.  Successful attacks of this vulnerability can result in  unauthorized creation, deletion or modification access to critical data or all Oracle Java SE accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 5.9 (Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22043
- https://openjdk.org/groups/vulnerability/advisories/2023-07-18
- https://security.netapp.com/advisory/ntap-20230725-0006/
- https://www.oracle.com/security-alerts/cpujul2023.html
