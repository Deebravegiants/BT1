# [M] BIT-java-2020-14556

## Summary
Severity: Medium
Advisory: BIT-java-2020-14556
Aliases: BIT-java-min-2020-14556, BIT-jre-2020-14556, CVE-2020-14556
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-14556
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <14.0.2

## Details
Vulnerability in the Java SE, Java SE Embedded product of Oracle Java SE (component: Libraries). Supported versions that are affected are Java SE: 8u251, 11.0.7 and 14.0.1; Java SE Embedded: 8u251. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Java SE Embedded. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Java SE, Java SE Embedded accessible data as well as unauthorized read access to a subset of Java SE, Java SE Embedded accessible data. Note: Applies to client and server deployment of Java. This vulnerability can be exploited through sandboxed Java Web Start applications and sandboxed Java applets. It can also be exploited by supplying data to APIs in the specified Component without using sandboxed Java Web Start applications or sandboxed Java applets, such as through a web service. CVSS 3.1 Base Score 4.8 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00041.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6CFJPOYF3CWYEPCDOAOCNFJTQIKKWPHW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DFZ36XIW5ENQAW6BB7WHRFFTTJX7KGMR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MEPHBZPNSLX43B26DWKB7OS6AROTS2BO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QQUMIAON2YEFRONMIUVHAKYCIOLICDBA/
- https://nvd.nist.gov/vuln/detail/CVE-2020-14556
- https://security.gentoo.org/glsa/202008-24
- https://security.gentoo.org/glsa/202209-15
- https://security.netapp.com/advisory/ntap-20200717-0005/
- https://usn.ubuntu.com/4433-1/
- https://usn.ubuntu.com/4453-1/
- https://www.debian.org/security/2020/dsa-4734
- https://www.oracle.com/security-alerts/cpujul2020.html
