# [M] Improper Limitation of a Pathname to a Restricted Directory in JCraft JSch

## Summary
Severity: Medium
Advisory: GHSA-q446-82vq-w674
CVE: CVE-2016-5725
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q446-82vq-w674
Type: github-advisory

## Affected
- Maven: `com.jcraft:jsch` — affected >=0 <0.1.54

## Details
Directory traversal vulnerability in JCraft JSch before 0.1.54 on Windows, when the mode is ChannelSftp.OVERWRITE, allows remote SFTP servers to write to arbitrary files via a ..\ (dot dot backslash) in a response to a recursive GET command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5725
- https://access.redhat.com/errata/RHSA-2017:3115
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2016-5725
- https://lists.debian.org/debian-lts-announce/2020/04/msg00017.html
- https://www.exploit-db.com/exploits/40411
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://packetstormsecurity.com/files/138809/jsch-0.1.53-Path-Traversal.html
- http://seclists.org/fulldisclosure/2016/Sep/53
- http://www.jcraft.com/jsch/ChangeLog
