# [H] CVE-2019-20044

## Summary
Severity: High
Advisory: CVE-2019-20044
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/CVE-2019-20044
Type: osv

## Details
In Zsh before 5.8, attackers able to execute commands can regain privileges dropped by the --no-PRIVILEGED option. Zsh fails to overwrite the saved uid, so the original privileges can be restored by executing MODULE_PATH=/dir/with/module zmodload with a module that calls setuid().

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PN5V7MPHRRP7QNHOEK56S7QGRU53WUN6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FP64FFIZI2CKQOEAOI5A72PVQULE7ZZC/
- http://seclists.org/fulldisclosure/2020/May/49
- https://lists.debian.org/debian-lts-announce/2020/12/msg00000.html
- https://support.apple.com/HT211168
- https://support.apple.com/HT211171
- http://seclists.org/fulldisclosure/2020/May/53
- http://seclists.org/fulldisclosure/2020/May/55
- http://seclists.org/fulldisclosure/2020/May/59
- https://security.gentoo.org/glsa/202003-55
- http://zsh.sourceforge.net/releases.html
- https://support.apple.com/HT211170
- https://support.apple.com/kb/HT211168
- https://support.apple.com/kb/HT211171
- https://www.zsh.org/mla/zsh-announce/141
- https://lists.debian.org/debian-lts-announce/2020/03/msg00004.html
- https://support.apple.com/HT211175
- https://support.apple.com/kb/HT211170
- https://support.apple.com/kb/HT211175
- https://github.com/XMB5/zsh-privileged-upgrade
