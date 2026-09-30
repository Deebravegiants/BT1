# [H] Insecure Deserialization in Apache Commons Beanutils

## Summary
Severity: High
Advisory: GHSA-6phf-73q6-gh87
CVE: CVE-2019-10086
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-6phf-73q6-gh87
Type: github-advisory

## Affected
- Maven: `commons-beanutils:commons-beanutils` — affected >=0 <1.9.4

## Details
In Apache Commons Beanutils 1.9.2, a special BeanIntrospector class was added which allows suppressing the ability for an attacker to access the classloader via the class property available on all Java objects. We, however were not using this by default characteristic of the PropertyUtilsBean.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10086
- https://access.redhat.com/errata/RHSA-2019:4317
- https://lists.apache.org/thread.html/ra41fd0ad4b7e1d675c03a5081a16a6603085a4e37d30b866067566fe@%3Cissues.nifi.apache.org%3E
- https://lists.apache.org/thread.html/ra87ac17410a62e813cba901fdd4e9a674dd53daaf714870f28e905f1@%3Cdev.atlas.apache.org%3E
- https://lists.apache.org/thread.html/ra9a139fdc0999750dcd519e81384bc1fe3946f311b1796221205f51c@%3Ccommits.dolphinscheduler.apache.org%3E
- https://lists.apache.org/thread.html/racd3e7b2149fa2f255f016bd6bffab0fea77b6fb81c50db9a17f78e6@%3Cdev.atlas.apache.org%3E
- https://lists.apache.org/thread.html/rae81e0c8ebdf47ffaa85a01240836bfece8a990c48f55c7933162b5c@%3Cdev.atlas.apache.org%3E
- https://lists.apache.org/thread.html/rb1f76c2c0a4d6efb8a3523974f9d085d5838b73e7bffdf9a8f212997@%3Cissues.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rb8dac04cb7e9cc5dedee8dabaa1c92614f590642e5ebf02a145915ba@%3Ccommits.atlas.apache.org%3E
- https://lists.apache.org/thread.html/rcc029be4edaaf5b8bb85818aab494e16f312fced07a0f4a202771ba2@%3Cissues.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rd2d2493f4f1af6980d265b8d84c857e2b7ab80a46e1423710c448957@%3Cissues.nifi.apache.org%3E
- https://lists.apache.org/thread.html/re2028d4d76ba1db3e3c3a722d6c6034e801cc3b309f69cc166eaa32b@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/re3cd7cb641d7fc6684e4fc3c336a8bad4a01434bb5625a06e3600fd1@%3Cissues.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rec74f3a94dd850259c730b4ba6f7b6211222b58900ec088754aa0534@%3Cissues.nifi.apache.org%3E
- https://lists.apache.org/thread.html/reee57101464cf7622d640ae013b2162eb864f603ec4093de8240bb8f@%3Cdev.atlas.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2019/08/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4APPGLBWMFAS4WHNLR4LIJ65DJGPV7TF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JIUYSL2RSIWZVNSUIXJTIFPIPIF6OAIO
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
