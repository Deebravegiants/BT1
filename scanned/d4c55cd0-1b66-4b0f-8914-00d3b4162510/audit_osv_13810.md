# [M] CVE-2018-2799

## Summary
Severity: Medium
Advisory: CVE-2018-2799
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-04-19
Source: https://osv.dev/vulnerability/CVE-2018-2799
Type: osv

## Details
Vulnerability in the Java SE, Java SE Embedded, JRockit component of Oracle Java SE (subcomponent: JAXP). Supported versions that are affected are Java SE: 7u171, 8u162 and 10; Java SE Embedded: 8u161; JRockit: R28.3.17. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise Java SE, Java SE Embedded, JRockit. Successful attacks of this vulnerability can result in unauthorized ability to cause a partial denial of service (partial DOS) of Java SE, Java SE Embedded, JRockit. Note: Applies to client and server deployment of Java. This vulnerability can be exploited through sandboxed Java Web Start applications and sandboxed Java applets. It can also be exploited by supplying data to APIs in the specified Component without using sandboxed Java Web Start applications or sandboxed Java applets, such as through a web service. CVSS 3.0 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L).

## References
- http://www.securityfocus.com/bid/103872
- http://www.securitytracker.com/id/1040697
- https://access.redhat.com/errata/RHSA-2018:1188
- https://access.redhat.com/errata/RHSA-2018:1191
- https://access.redhat.com/errata/RHSA-2018:1201
- https://access.redhat.com/errata/RHSA-2018:1202
- https://access.redhat.com/errata/RHSA-2018:1204
- https://access.redhat.com/errata/RHSA-2018:1206
- https://access.redhat.com/errata/RHSA-2018:1270
- https://access.redhat.com/errata/RHSA-2018:1278
- https://access.redhat.com/errata/RHSA-2018:1721
- https://access.redhat.com/errata/RHSA-2018:1722
- https://access.redhat.com/errata/RHSA-2018:1723
- https://access.redhat.com/errata/RHSA-2018:1724
- https://access.redhat.com/errata/RHSA-2018:1974
- https://access.redhat.com/errata/RHSA-2018:1975
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://lists.apache.org/thread.html/b53d4601ecd9ec63c799dbe1bc5b78e0d52f4cef429da2dfe63cf06d%40%3Cfop-dev.xmlgraphics.apache.org%3E
- https://lists.apache.org/thread.html/r449b5d89c7b2ba3762584cf6c38e01867d4b24706e023cf2a9911307%40%3Cuser.spark.apache.org%3E
- https://security.gentoo.org/glsa/201903-14
