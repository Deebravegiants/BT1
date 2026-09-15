# [H] BIT-java-2020-2604

## Summary
Severity: High
Advisory: BIT-java-2020-2604
Aliases: BIT-java-min-2020-2604, BIT-jre-2020-2604, CVE-2020-2604
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2020-2604
Type: osv

## Affected
- Bitnami: `java` — affected >=12.0.0 <13.0.2

## Details
Vulnerability in the Java SE, Java SE Embedded product of Oracle Java SE (component: Serialization). Supported versions that are affected are Java SE: 7u241, 8u231, 11.0.5 and 13.0.1; Java SE Embedded: 8u231. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Java SE Embedded. Successful attacks of this vulnerability can result in takeover of Java SE, Java SE Embedded. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets (in Java SE 8), that load and run untrusted code (e.g., code that comes from the internet) and rely on the Java sandbox for security. This vulnerability can also be exploited by using APIs in the specified Component, e.g., through a web service which supplies data to the APIs. CVSS v3.0 Base Score 8.1 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00060.html
- https://access.redhat.com/errata/RHSA-2020:0122
- https://access.redhat.com/errata/RHSA-2020:0128
- https://access.redhat.com/errata/RHSA-2020:0196
- https://access.redhat.com/errata/RHSA-2020:0202
- https://access.redhat.com/errata/RHSA-2020:0231
- https://access.redhat.com/errata/RHSA-2020:0232
- https://access.redhat.com/errata/RHSA-2020:0465
- https://access.redhat.com/errata/RHSA-2020:0467
- https://access.redhat.com/errata/RHSA-2020:0468
- https://access.redhat.com/errata/RHSA-2020:0469
- https://access.redhat.com/errata/RHSA-2020:0470
- https://access.redhat.com/errata/RHSA-2020:0541
- https://access.redhat.com/errata/RHSA-2020:0632
- https://kc.mcafee.com/corporate/index?page=content&id=SB10315
- https://lists.debian.org/debian-lts-announce/2020/02/msg00034.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-2604
- https://seclists.org/bugtraq/2020/Feb/22
- https://security.gentoo.org/glsa/202101-19
