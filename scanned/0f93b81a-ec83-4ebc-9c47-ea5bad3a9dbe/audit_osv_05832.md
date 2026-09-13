# [H] BIT-java-2020-14593

## Summary
Severity: High
Advisory: BIT-java-2020-14593
Aliases: BIT-java-min-2020-14593, BIT-jre-2020-14593, CVE-2020-14593
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-14593
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <14.0.2

## Details
Vulnerability in the Java SE, Java SE Embedded product of Oracle Java SE (component: 2D). Supported versions that are affected are Java SE: 7u261, 8u251, 11.0.7 and 14.0.1; Java SE Embedded: 8u251. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Java SE Embedded. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in Java SE, Java SE Embedded, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all Java SE, Java SE Embedded accessible data. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets, that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g., code installed by an administrator). CVSS 3.1 Base Score 7.4 (Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00041.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFJPOYF3CWYEPCDOAOCNFJTQIKKWPHW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DFZ36XIW5ENQAW6BB7WHRFFTTJX7KGMR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MEPHBZPNSLX43B26DWKB7OS6AROTS2BO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QQUMIAON2YEFRONMIUVHAKYCIOLICDBA/
- https://nvd.nist.gov/vuln/detail/CVE-2020-14593
- https://security.gentoo.org/glsa/202008-24
- https://security.gentoo.org/glsa/202209-15
- https://security.netapp.com/advisory/ntap-20200717-0005/
- https://usn.ubuntu.com/4433-1/
- https://usn.ubuntu.com/4453-1/
- https://www.debian.org/security/2020/dsa-4734
- https://www.oracle.com/security-alerts/cpujul2020.html
