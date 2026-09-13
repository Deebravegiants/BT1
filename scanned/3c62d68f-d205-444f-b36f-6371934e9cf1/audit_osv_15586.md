# [C] CVE-2019-17531

## Summary
Severity: Critical
Advisory: CVE-2019-17531
Aliases: GHSA-gjmw-vf9h-g25v
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-12
Source: https://osv.dev/vulnerability/CVE-2019-17531
Type: osv

## Details
A Polymorphic Typing issue was discovered in FasterXML jackson-databind 2.0.0 through 2.9.10. When Default Typing is enabled (either globally or for a specific property) for an externally exposed JSON endpoint and the service has the apache-log4j-extra (version 1.2.x) jar in the classpath, and an attacker can provide a JNDI service to access, it is possible to make the service execute a malicious payload.

## References
- https://lists.apache.org/thread.html/b3c90d38f99db546de60fea65f99a924d540fae2285f014b79606ca5%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r392099ed2757ff2e383b10440594e914d080511d7da1c8fed0612c1f%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rf1bbc0ea4a9f014cf94df9a12a6477d24a27f52741dbc87f2fd52ff2%40%3Cissues.geode.apache.org%3E
- https://medium.com/%40cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://access.redhat.com/errata/RHSA-2019:4192
- https://access.redhat.com/errata/RHSA-2020:0159
- https://access.redhat.com/errata/RHSA-2020:0160
- https://access.redhat.com/errata/RHSA-2020:0161
- https://access.redhat.com/errata/RHSA-2020:0164
- https://access.redhat.com/errata/RHSA-2020:0445
- https://lists.debian.org/debian-lts-announce/2019/12/msg00013.html
- https://security.netapp.com/advisory/ntap-20191024-0005/
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://github.com/FasterXML/jackson-databind/issues/2498
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
