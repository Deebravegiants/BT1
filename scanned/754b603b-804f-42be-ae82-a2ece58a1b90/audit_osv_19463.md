# [C] CVE-2021-21350

## Summary
Severity: Critical
Advisory: CVE-2021-21350
Aliases: BIT-activemq-2021-21350, GHSA-43gc-mjxg-gvrq
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/CVE-2021-21350
Type: osv

## Details
XStream is a Java library to serialize objects to XML and back again. In XStream before version 1.4.16, there is a vulnerability which may allow a remote attacker to execute arbitrary code only by manipulating the processed input stream. No user is affected, who followed the recommendation to setup XStream's security framework with a whitelist limited to the minimal required types. If you rely on XStream's default blacklist of the Security Framework, you will have to use at least version 1.4.16.

## References
- http://x-stream.github.io/changes.html#1.4.16
- https://github.com/x-stream/xstream/security/advisories/GHSA-43gc-mjxg-gvrq
- https://lists.debian.org/debian-lts-announce/2021/04/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB/
- https://security.netapp.com/advisory/ntap-20210430-0002/
- https://www.debian.org/security/2021/dsa-5004
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://x-stream.github.io/security.html#workaround
- https://lists.apache.org/thread.html/r8244fd0831db894d5e89911ded9c72196d395a90ae655414d23ed0dd%40%3Cusers.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r9ac71b047767205aa22e3a08cb33f3e0586de6b2fac48b425c6e16b0%40%3Cdev.jmeter.apache.org%3E
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://x-stream.github.io/CVE-2021-21350.html
