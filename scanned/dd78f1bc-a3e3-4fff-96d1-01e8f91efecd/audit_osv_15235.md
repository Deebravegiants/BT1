# [H] CVE-2019-14744

## Summary
Severity: High
Advisory: CVE-2019-14744
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-07
Source: https://osv.dev/vulnerability/CVE-2019-14744
Type: osv

## Details
In KDE Frameworks KConfig before 5.61.0, malicious desktop files and configuration files lead to code execution with minimal user interaction. This relates to libKF5ConfigCore.so, and the mishandling of .desktop and .directory files, as demonstrated by a shell command on an Icon line in a .desktop file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5IRIKH7ZWXELIQT6WSLV7EG3VTFWKZPD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FNHO6FZRYBQ2R3UCFDGS66F6DNNTKCMM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UYKLUSSEK3YJOVQDL6K2LKGS3354UH6L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTFBQRJAU7ITD3TOMPZAUQMYYCAZ6DTX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YIDXQ6CUB5E7Y3MJWCUY4VR42QAE6SCJ/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00034.html
- https://access.redhat.com/errata/RHSA-2019:2606
- https://lists.debian.org/debian-lts-announce/2019/08/msg00023.html
- https://seclists.org/bugtraq/2019/Aug/12
- https://seclists.org/bugtraq/2019/Aug/9
- https://security.gentoo.org/glsa/201908-07
- https://usn.ubuntu.com/4100-1/
- https://www.debian.org/security/2019/dsa-4494
- https://www.zdnet.com/article/unpatched-kde-vulnerability-disclosed-on-twitter/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00016.html
- http://packetstormsecurity.com/files/153981/Slackware-Security-Advisory-kdelibs-Updates.html
- https://gist.githubusercontent.com/zeropwn/630832df151029cb8f22d5b6b9efaefb/raw/64aa3d30279acb207f787ce9c135eefd5e52643b/kde-kdesktopfile-command-injection.txt
