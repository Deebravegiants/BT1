# [H] BIT-java-2020-2805

## Summary
Severity: High
Advisory: BIT-java-2020-2805
Aliases: BIT-java-min-2020-2805, BIT-jre-2020-2805, CVE-2020-2805
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-2805
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <14.0.1

## Details
Vulnerability in the Java SE, Java SE Embedded product of Oracle Java SE (component: Libraries). Supported versions that are affected are Java SE: 7u251, 8u241, 11.0.6 and 14; Java SE Embedded: 8u241. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Java SE Embedded. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in Java SE, Java SE Embedded, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in takeover of Java SE, Java SE Embedded. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.0 Base Score 8.3 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00048.html
- https://lists.debian.org/debian-lts-announce/2020/04/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CKAV6KFFAEANXAN73AFTGU7Z6YNRWCXQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L7VHC4EW36KZEIDQ56RPCWBZCQELFFKN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NYHHHZRHXCBGRHGE5UP7UEB4IZ2QX536/
- https://nvd.nist.gov/vuln/detail/CVE-2020-2805
- https://security.gentoo.org/glsa/202006-22
- https://security.gentoo.org/glsa/202209-15
- https://security.netapp.com/advisory/ntap-20200416-0004/
- https://usn.ubuntu.com/4337-1/
- https://www.debian.org/security/2020/dsa-4662
- https://www.debian.org/security/2020/dsa-4668
- https://www.oracle.com/security-alerts/cpuapr2020.html
