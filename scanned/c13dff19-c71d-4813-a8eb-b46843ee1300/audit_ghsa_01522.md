# [C] XML external entity injection in Terracotta Quartz Scheduler

## Summary
Severity: Critical
Advisory: GHSA-9qcf-c26r-x5rf
CVE: CVE-2019-13990
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-01
Source: https://github.com/advisories/GHSA-9qcf-c26r-x5rf
Type: github-advisory

## Affected
- Maven: `org.quartz-scheduler:quartz` — affected >=0 <2.3.2

## Details
initDocumentParser in xml/XMLSchedulingDataProcessor.java in Terracotta Quartz Scheduler through 2.3.0 allows XXE attacks via a job description.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13990
- https://github.com/quartz-scheduler/quartz/issues/467
- https://github.com/quartz-scheduler/quartz/pull/501
- https://github.com/quartz-scheduler/quartz/commit/13c1d45aa1db15d0fa0e4997139c99ba219be551
- https://lists.apache.org/thread.html/r21df13c8bd2c2eae4b9661aae814c4a2a814d1f7875c765b8b115c9a@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r3a6884e8d819f32cde8c07b98934de3e80467859880f784950bf44cf%40%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r3a6884e8d819f32cde8c07b98934de3e80467859880f784950bf44cf@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/re9b56ac1934d7bf16afc83eac1c39c98c1b20b4b15891dce923bf8aa%40%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/re9b56ac1934d7bf16afc83eac1c39c98c1b20b4b15891dce923bf8aa@%3Ccommits.tomee.apache.org%3E
- https://security.netapp.com/advisory/ntap-20221028-0002
- https://snyk.io/vuln/SNYK-JAVA-ORGQUARTZSCHEDULER-461170
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://lists.apache.org/thread.html/r21df13c8bd2c2eae4b9661aae814c4a2a814d1f7875c765b8b115c9a%40%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/f74b170d3d58d7a24db1afd3908bb0ab58a3900e16e73275674cdfaf@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/f74b170d3d58d7a24db1afd3908bb0ab58a3900e16e73275674cdfaf%40%3Ccommits.tomee.apache.org%3E
