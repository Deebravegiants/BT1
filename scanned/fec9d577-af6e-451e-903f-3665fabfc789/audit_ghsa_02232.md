# [H] XStream is vulnerable to a Remote Command Execution attack

## Summary
Severity: High
Advisory: GHSA-j9h8-phrw-h4fh
CVE: CVE-2021-39144
CWE: CWE-306, CWE-502, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-j9h8-phrw-h4fh
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.18

## Details
### Impact
The vulnerability may allow a remote attacker has sufficient rights to execute commands of the host only by manipulating the processed input stream. No user is affected, who followed the recommendation to setup XStream's security framework with a whitelist limited to the minimal required types.

### Patches
XStream 1.4.18 uses no longer a blacklist by default, since it cannot be secured for general purpose.

### Workarounds
See [workarounds](https://x-stream.github.io/security.html#workaround) for the different versions covering all CVEs.

### References
See full information about the nature of the vulnerability and the steps to reproduce it in XStream's documentation for [CVE-2021-39144](https://x-stream.github.io/CVE-2021-39144.html).

### Credits

Ceclin and YXXX from the Tencent Security Response Center found and reported the issue to XStream and provided the required information to reproduce it.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [XStream](https://github.com/x-stream/xstream/issues)
* Email us at [XStream Google Group](https://groups.google.com/group/xstream-user)

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-j9h8-phrw-h4fh
- https://nvd.nist.gov/vuln/detail/CVE-2021-39144
- https://x-stream.github.io/CVE-2021-39144.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.debian.org/security/2021/dsa-5004
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-39144
- https://security.netapp.com/advisory/ntap-20210923-0003
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP
- https://lists.debian.org/debian-lts-announce/2021/09/msg00017.html
- https://github.com/x-stream/xstream
- http://packetstormsecurity.com/files/169859/VMware-NSX-Manager-XStream-Unauthenticated-Remote-Code-Execution.html
