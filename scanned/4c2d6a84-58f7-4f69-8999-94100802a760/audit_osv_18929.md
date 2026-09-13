# [H] CVE-2020-5208

## Summary
Severity: High
Advisory: CVE-2020-5208
Aliases: GHSA-g659-9qxw-p7cp
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-05
Source: https://osv.dev/vulnerability/CVE-2020-5208
Type: osv

## Details
It's been found that multiple functions in ipmitool before 1.8.19 neglect proper checking of the data received from a remote LAN party, which may lead to buffer overflows and potentially to remote code execution on the ipmitool side. This is especially dangerous if ipmitool is run as a privileged user. This problem is fixed in version 1.8.19.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K2BPW66KDP4H36AGZXLED57A3O2Y6EQW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RYYEKUAUTCWICM77HOEGZDVVEUJLP4BP/
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00031.html
- https://lists.debian.org/debian-lts-announce/2020/02/msg00006.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00029.html
- https://security.gentoo.org/glsa/202101-03
- https://github.com/ipmitool/ipmitool/commit/e824c23316ae50beb7f7488f2055ac65e8b341f2
- https://github.com/ipmitool/ipmitool/security/advisories/GHSA-g659-9qxw-p7cp
