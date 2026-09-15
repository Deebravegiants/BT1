# [M] XStream can cause a Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-6wf9-jmg9-vxcc
CVE: CVE-2021-39140
CWE: CWE-502, CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6wf9-jmg9-vxcc
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.18

## Details
### Impact
The vulnerability may allow a remote attacker to allocate 100% CPU time on the target system depending on CPU type or parallel execution of such a payload resulting in a denial of service only by manipulating the processed input stream. No user is affected, who followed the recommendation to setup XStream's security framework with a whitelist limited to the minimal required types.

### Patches
XStream 1.4.18 uses no longer a blacklist by default, since it cannot be secured for general purpose.

### Workarounds
See [workarounds](https://x-stream.github.io/security.html#workaround) for the different versions covering all CVEs.

### References
See full information about the nature of the vulnerability and the steps to reproduce it in XStream's documentation for [CVE-2021-39140](https://x-stream.github.io/CVE-2021-39140.html).

### Credits
The vulnerability was discovered and reported by Lai Han of nsfocus security team.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [XStream](https://github.com/x-stream/xstream/issues)
* Contact us at [XStream Google Group](https://groups.google.com/group/xstream-user)

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-6wf9-jmg9-vxcc
- https://nvd.nist.gov/vuln/detail/CVE-2021-39140
- https://github.com/x-stream/xstream
- https://lists.debian.org/debian-lts-announce/2021/09/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB
- https://security.netapp.com/advisory/ntap-20210923-0003
- https://www.debian.org/security/2021/dsa-5004
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://x-stream.github.io/CVE-2021-39140.html
