# [H] CVE-2021-39150

## Summary
Severity: High
Advisory: CVE-2021-39150
Aliases: GHSA-cxfm-5m4g-x7xp
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2021-39150
Type: osv

## Details
XStream is a simple library to serialize objects to XML and back again. In affected versions this vulnerability may allow a remote attacker to request data from internal resources that are not publicly available only by manipulating the processed input stream with a Java runtime version 14 to 8. No user is affected, who followed the recommendation to setup XStream's security framework with a whitelist limited to the minimal required types. If you rely on XStream's default blacklist of the [Security Framework](https://x-stream.github.io/security.html#framework), you will have to use at least version 1.4.18.

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-cxfm-5m4g-x7xp
- https://lists.debian.org/debian-lts-announce/2021/09/msg00017.html
- https://security.netapp.com/advisory/ntap-20210923-0003/
- https://www.debian.org/security/2021/dsa-5004
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB/
- https://x-stream.github.io/CVE-2021-39150.html
