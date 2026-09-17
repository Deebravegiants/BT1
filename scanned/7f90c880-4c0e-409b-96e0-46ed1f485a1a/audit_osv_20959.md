# [H] CVE-2021-39153

## Summary
Severity: High
Advisory: CVE-2021-39153
Aliases: GHSA-2q8x-2p7f-574v
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2021-39153
Type: osv

## Details
XStream is a simple library to serialize objects to XML and back again. In affected versions this vulnerability may allow a remote attacker to load and execute arbitrary code from a remote host only by manipulating the processed input stream, if using the version out of the box with Java runtime version 14 to 8 or with JavaFX installed. No user is affected, who followed the recommendation to setup XStream's security framework with a whitelist limited to the minimal required types. XStream 1.4.18 uses no longer a blacklist by default, since it cannot be secured for general purpose.

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-2q8x-2p7f-574v
- https://lists.debian.org/debian-lts-announce/2021/09/msg00017.html
- https://security.netapp.com/advisory/ntap-20210923-0003/
- https://www.debian.org/security/2021/dsa-5004
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB/
- https://x-stream.github.io/CVE-2021-39153.html
