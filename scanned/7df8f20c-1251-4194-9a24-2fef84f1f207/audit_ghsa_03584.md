# [M] XStream is vulnerable to an attack using Regular Expression for a Denial of Service (ReDos)

## Summary
Severity: Medium
Advisory: GHSA-56p8-3fh9-4cvq
CVE: CVE-2021-21348
CWE: CWE-400, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-22
Source: https://github.com/advisories/GHSA-56p8-3fh9-4cvq
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.16

## Details
### Impact
The vulnerability may allow a remote attacker to occupy a thread that consumes maximum CPU time and will never return. No user is affected, who followed the recommendation to setup XStream's security framework with a whitelist limited to the minimal required types.

### Patches
If you rely on XStream's default blacklist of the [Security Framework](https://x-stream.github.io/security.html#framework), you will have to use at least version 1.4.16.

### Workarounds
See [workarounds](https://x-stream.github.io/security.html#workaround) for the different versions covering all CVEs.

### References
See full information about the nature of the vulnerability and the steps to reproduce it in XStream's documentation for [CVE-2021-21348](https://x-stream.github.io/CVE-2021-21348.html).

### Credits
The vulnerability was discovered and reported by threedr3am.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [XStream](https://github.com/x-stream/xstream/issues)
* Contact us at [XStream Google Group](https://groups.google.com/group/xstream-user)

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-56p8-3fh9-4cvq
- https://nvd.nist.gov/vuln/detail/CVE-2021-21348
- https://github.com/x-stream/xstream
- https://lists.apache.org/thread.html/r8244fd0831db894d5e89911ded9c72196d395a90ae655414d23ed0dd@%3Cusers.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r9ac71b047767205aa22e3a08cb33f3e0586de6b2fac48b425c6e16b0@%3Cdev.jmeter.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/04/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB
- https://security.netapp.com/advisory/ntap-20210430-0002
- https://www.debian.org/security/2021/dsa-5004
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://x-stream.github.io/CVE-2021-21348.html
- https://x-stream.github.io/security.html#workaround
- http://x-stream.github.io/changes.html#1.4.16
