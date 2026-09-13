# [H] CVE-2019-1000018

## Summary
Severity: High
Advisory: CVE-2019-1000018
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-1000018
Type: osv

## Details
rssh version 2.3.4 contains a CWE-77: Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in allowscp permission that can result in Local command execution. This attack appear to be exploitable via An authorized SSH user with the allowscp permission.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KR2OHTHMJVV4DO3HDRFQQZ5JENHDJQEN/
- https://github.com/WlX-33/PoC-for-CVE/blob/main/CVE-2021-33216%2CCVE-2019-1000018/CommScope%20Ruckus%20IoT%20Controller%201.7.1.0%20Undocumented%20Account.txt
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HO3MDU3AH5SLYBKHH5PJ6PHC63ASIF42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HO3MDU3AH5SLYBKHH5PJ6PHC63ASIF42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T42YYNWJZG422GATWAHAEK4A24OKY557/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KR2OHTHMJVV4DO3HDRFQQZ5JENHDJQEN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T42YYNWJZG422GATWAHAEK4A24OKY557/
- https://usn.ubuntu.com/3946-1/
- https://www.debian.org/security/2019/dsa-4377
- https://security.gentoo.org/glsa/202007-29
- http://seclists.org/fulldisclosure/2021/May/78
- https://lists.debian.org/debian-lts-announce/2019/01/msg00027.html
- https://esnet-security.github.io/vulnerabilities/20190115_rssh
