# [H] CVE-2018-3169

## Summary
Severity: High
Advisory: CVE-2018-3169
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-3169
Type: osv

## Details
Vulnerability in the Java SE, Java SE Embedded component of Oracle Java SE (subcomponent: Hotspot). Supported versions that are affected are Java SE: 7u191, 8u182 and 11; Java SE Embedded: 8u181. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Java SE Embedded. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in Java SE, Java SE Embedded, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in takeover of Java SE, Java SE Embedded. Note: This vulnerability applies to Java deployments, typically in clients running sandboxed Java Web Start applications or sandboxed Java applets (in Java SE 8), that load and run untrusted code (e.g. code that comes from the internet) and rely on the Java sandbox for security. This vulnerability does not apply to Java deployments, typically in servers, that load and run only trusted code (e.g. code installed by an administrator). CVSS 3.0 Base Score 8.3 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H).

## References
- http://www.securityfocus.com/bid/105587
- https://access.redhat.com/errata/RHSA-2018:3000
- https://access.redhat.com/errata/RHSA-2018:3409
- https://access.redhat.com/errata/RHSA-2018:3672
- https://www.debian.org/security/2018/dsa-4326
- https://access.redhat.com/errata/RHSA-2018:3534
- https://access.redhat.com/errata/RHSA-2018:2943
- https://access.redhat.com/errata/RHSA-2018:3001
- https://access.redhat.com/errata/RHSA-2018:3003
- https://security.gentoo.org/glsa/201908-10
- https://security.netapp.com/advisory/ntap-20181018-0001/
- http://www.securitytracker.com/id/1041889
- https://access.redhat.com/errata/RHSA-2018:2942
- https://access.redhat.com/errata/RHSA-2018:3671
- https://access.redhat.com/errata/RHSA-2018:3779
- https://access.redhat.com/errata/RHSA-2018:3852
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbst03952en_us
- https://usn.ubuntu.com/3824-1/
- https://access.redhat.com/errata/RHSA-2018:3002
- https://access.redhat.com/errata/RHSA-2018:3350
