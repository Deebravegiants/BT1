# [H] BIT-java-2021-2388

## Summary
Severity: High
Advisory: BIT-java-2021-2388
Aliases: BIT-java-min-2021-2388, BIT-jre-2021-2388, CVE-2021-2388
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2021-2388
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <16.0.2

## Details
Vulnerability in the Java SE, Oracle GraalVM Enterprise Edition product of Oracle Java SE (component: Hotspot). Supported versions that are affected are Java SE: 8u291, 11.0.11, 16.0.1; Oracle GraalVM Enterprise Edition: 20.3.2 and 21.1.0. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Oracle GraalVM Enterprise Edition. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in takeover of Java SE, Oracle GraalVM Enterprise Edition. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 7.5 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H).

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00011.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-2388
- https://security.gentoo.org/glsa/202209-05
- https://security.netapp.com/advisory/ntap-20210723-0002/
- https://www.debian.org/security/2021/dsa-4946
- https://www.oracle.com/security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
