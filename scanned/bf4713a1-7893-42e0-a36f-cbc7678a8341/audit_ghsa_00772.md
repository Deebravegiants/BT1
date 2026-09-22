# [H] RFD attack via Content-Disposition header sourced from request input by Spring MVC or Spring WebFlux Application

## Summary
Severity: High
Advisory: GHSA-8wx2-9q48-vm9r
CVE: CVE-2020-5398
CWE: CWE-494, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-21
Source: https://github.com/advisories/GHSA-8wx2-9q48-vm9r
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=5.2.0.RELEASE <5.2.3.RELEASE
- Maven: `org.springframework:spring-webmvc` — affected >=5.1.0.RELEASE <5.1.13.RELEASE
- Maven: `org.springframework:spring-webmvc` — affected >=5.0.0.RELEASE <5.0.16.RELEASE
- Maven: `org.springframework:spring-webflux` — affected >=5.2.0.RELEASE <5.2.3.RELEASE
- Maven: `org.springframework:spring-webflux` — affected >=5.1.0.RELEASE <5.1.13.RELEASE
- Maven: `org.springframework:spring-webflux` — affected >=5.0.0.RELEASE <5.0.16.RELEASE

## Details
In Spring Framework, versions 5.2.x prior to 5.2.3, versions 5.1.x prior to 5.1.13, and versions 5.0.x prior to 5.0.16, an application is vulnerable to a reflected file download (RFD) attack when it sets a "Content-Disposition" header in the response where the filename attribute is derived from user supplied input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5398
- https://github.com/spring-projects/spring-framework/commit/41f40c6c229d3b4f768718f1ec229d8f0ad76d76
- https://lists.apache.org/thread.html/r8cc37a60a5056351377ee5f1258f2a4fdd39822a257838ba6bcc1e88@%3Ccommits.karaf.apache.org%3E
- https://lists.apache.org/thread.html/r9f13cccb214495e14648d2c9b8f2c6072fd5219e74502dd35ede81e1@%3Cdev.ambari.apache.org%3E
- https://lists.apache.org/thread.html/r9fb1ee08cf337d16c3364feb0f35a072438c1a956afd7b77859aa090@%3Cissues.karaf.apache.org%3E
- https://lists.apache.org/thread.html/ra996b56e1f5ab2fed235a8b91fa0cc3cf34c2e9fee290b7fa4380a0d@%3Ccommits.servicecomb.apache.org%3E
- https://lists.apache.org/thread.html/rab0de39839b4c208dcd73f01e12899dc453361935a816a784548e048@%3Cissues.karaf.apache.org%3E
- https://lists.apache.org/thread.html/rb4d1fc078f086ec2e98b2693e8b358e58a6a4ef903ceed93a1ee2b18@%3Ccommits.karaf.apache.org%3E
- https://lists.apache.org/thread.html/rc05acaacad089613e9642f939b3a44f7199b5537493945c3e045287f@%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/rc9c7f96f08c8554225dba9050ea5e64bebc129d0d836303143fe3160@%3Cdev.rocketmq.apache.org%3E
- https://lists.apache.org/thread.html/rdcaadaa9a68b31b7d093d76eacfaacf6c7a819f976b595c75ad2d4dc@%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/rded5291e25a4c4085a6d43cf262e479140198bf4eabb84986e0a1ef3@%3Cdev.rocketmq.apache.org%3E
- https://lists.apache.org/thread.html/reaa8a6674baf2724b1b88a621b0d72d9f7a6f5577c88759842c16eb6@%3Ccommits.karaf.apache.org%3E
- https://lists.apache.org/thread.html/rf8dc72b974ee74f17bce661ea7d124e733a1f4c4f236354ac0cf48e8@%3Ccommits.camel.apache.org%3E
- https://pivotal.io/security/cve-2020-5398
- https://security.netapp.com/advisory/ntap-20210917-0006
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
