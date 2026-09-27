# [M] BIT-java-2020-14792

## Summary
Severity: Medium
Advisory: BIT-java-2020-14792
Aliases: BIT-java-min-2020-14792, BIT-jre-2020-14792, CVE-2020-14792
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-14792
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <15.0.1

## Details
Vulnerability in the Java SE, Java SE Embedded product of Oracle Java SE (component: Hotspot). Supported versions that are affected are Java SE: 7u271, 8u261, 11.0.8 and 15; Java SE Embedded: 8u261. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Java SE Embedded. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of Java SE, Java SE Embedded accessible data as well as unauthorized read access to a subset of Java SE, Java SE Embedded accessible data. Note: Applies to client and server deployment of Java. This vulnerability can be exploited through sandboxed Java Web Start applications and sandboxed Java applets. It can also be exploited by supplying data to APIs in the specified Component without using sandboxed Java Web Start applications or sandboxed Java applets, such as through a web service. CVSS 3.1 Base Score 4.2 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00041.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00031.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-14792
- https://security.gentoo.org/glsa/202101-19
- https://security.netapp.com/advisory/ntap-20201023-0004/
- https://www.debian.org/security/2020/dsa-4779
- https://www.oracle.com/security-alerts/cpuoct2020.html
