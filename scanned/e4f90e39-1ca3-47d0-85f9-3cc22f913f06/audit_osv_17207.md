# [M] CVE-2020-13696

## Summary
Severity: Medium
Advisory: CVE-2020-13696
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/CVE-2020-13696
Type: osv

## Details
An issue was discovered in LinuxTV xawtv before 3.107. The function dev_open() in v4l-conf.c does not perform sufficient checks to prevent an unprivileged caller of the program from opening unintended filesystem paths. This allows a local attacker with access to the v4l-conf setuid-root program to test for the existence of arbitrary files and to trigger an open on arbitrary files with mode O_RDWR. To achieve this, relative path components need to be added to the device path, as demonstrated by a v4l-conf -c /dev/../root/.bash_history command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ELOXU5LXQSQOXX64D4BICZV3TQWOBXHC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I7XWAO7W2DGA6M52JGK2TDWUGF62Q2KY/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00013.html
- https://usn.ubuntu.com/4518-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00009.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00018.html
- http://www.openwall.com/lists/oss-security/2020/06/04/6
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2020-13696
- https://git.linuxtv.org/xawtv3.git/commit/?id=31f31f9cbaee7be806cba38e0ff5431bd44b20a3
- https://git.linuxtv.org/xawtv3.git/commit/?id=36dc44e68e5886339b4a0fbe3f404fb1a4fd2292
- https://git.linuxtv.org/xawtv3.git/commit/?id=8e3feea862db68d3ca0886f46cd99fab45d2db7c
