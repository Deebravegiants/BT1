# [M] Improper Input Validation in Spring Framework

## Summary
Severity: Medium
Advisory: GHSA-rv39-3qh7-9v7w
CVE: CVE-2020-5421
CWE: CWE-35
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-rv39-3qh7-9v7w
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-framework-bom` — affected >=5.2.0 <5.2.9
- Maven: `org.springframework:spring-framework-bom` — affected >=5.1.0 <5.1.18
- Maven: `org.springframework:spring-framework-bom` — affected >=5.0.0 <5.0.19
- Maven: `org.springframework:spring-framework-bom` — affected >=0 <4.3.29

## Details
In Spring Framework versions 5.2.0 - 5.2.8, 5.1.0 - 5.1.17, 5.0.0 - 5.0.18, 4.3.0 - 4.3.28, and older unsupported versions, the protections against RFD attacks from CVE-2015-5211 may be bypassed depending on the browser used through the use of a jsessionid path parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5421
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://tanzu.vmware.com/security/cve-2020-5421
- https://security.netapp.com/advisory/ntap-20210513-0009
- https://lists.apache.org/thread.html/rf00d8f4101a1c1ea4de6ea1e09ddf7472cfd306745c90d6da87ae074@%3Cdev.hive.apache.org%3E
- https://lists.apache.org/thread.html/re014a49d77f038ba70e5e9934d400af6653e8c9ac110d32b1254127e@%3Cdev.ranger.apache.org%3E
- https://lists.apache.org/thread.html/rd462a8b0dfab4c15e67c0672cd3c211ecd0e4f018f824082ed54f665@%3Cissues.hive.apache.org%3E
- https://lists.apache.org/thread.html/rc9efaf6db98bee19db1bc911d0fa442287dac5cb229d4aaa08b6a13d@%3Cissues.hive.apache.org%3E
- https://lists.apache.org/thread.html/rb18ed999153ef0f0cb7af03efe0046c42c7242fd77fbd884a75ecfdc@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/raf7ca57033e537e4f9d7df7f192fa6968c1e49409b2348e08d807ccb@%3Cuser.ignite.apache.org%3E
- https://lists.apache.org/thread.html/ra889d95141059c6cbe77dd80249bb488ae53b274b5f3abad09d9511d@%3Cuser.ignite.apache.org%3E
- https://lists.apache.org/thread.html/r9f13cccb214495e14648d2c9b8f2c6072fd5219e74502dd35ede81e1@%3Cdev.ambari.apache.org%3E
- https://lists.apache.org/thread.html/r918caad55dcc640a16753b00d8d6acb90b4e36de4b6156d0867246ec@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r8b496b1743d128e6861ee0ed3c3c48cc56c505b38f84fa5baf7ae33a@%3Cdev.ambari.apache.org%3E
- https://lists.apache.org/thread.html/r7e6a213eea7f04fc6d9e3bd6eb8d68c4df92a22e956e95cb2c482865@%3Cissues.hive.apache.org%3E
