# [H] CVE-2019-18634

## Summary
Severity: High
Advisory: CVE-2019-18634
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-29
Source: https://osv.dev/vulnerability/CVE-2019-18634
Type: osv

## Details
In Sudo before 1.8.26, if pwfeedback is enabled in /etc/sudoers, users can trigger a stack-based buffer overflow in the privileged sudo process. (pwfeedback is a default setting in Linux Mint and elementary OS; however, it is NOT the default for upstream and many other packages, and would exist only if enabled by an administrator.) The attacker needs to deliver a long string to the stdin of getln() in tgetpass.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00029.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I6TKF36KOQUVJNBHSVJFA7BU3CCEYD2F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IY6DZ7WMDKU4ZDML6MJLDAPG42B5WVUC/
- https://usn.ubuntu.com/4263-1/
- https://usn.ubuntu.com/4263-2/
- http://packetstormsecurity.com/files/156174/Slackware-Security-Advisory-sudo-Updates.html
- http://packetstormsecurity.com/files/156189/Sudo-1.8.25p-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2020/Jan/40
- http://www.openwall.com/lists/oss-security/2020/01/30/6
- http://www.openwall.com/lists/oss-security/2020/01/31/1
- http://www.openwall.com/lists/oss-security/2020/02/05/2
- https://access.redhat.com/errata/RHSA-2020:0487
- https://access.redhat.com/errata/RHSA-2020:0509
- https://access.redhat.com/errata/RHSA-2020:0540
- https://access.redhat.com/errata/RHSA-2020:0726
- https://lists.debian.org/debian-lts-announce/2020/02/msg00002.html
- https://seclists.org/bugtraq/2020/Feb/2
- https://seclists.org/bugtraq/2020/Feb/3
- https://seclists.org/bugtraq/2020/Jan/44
- https://security.gentoo.org/glsa/202003-12
