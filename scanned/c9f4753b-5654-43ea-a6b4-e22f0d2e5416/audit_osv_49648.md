# [M] CVE-2019-15118

## Summary
Severity: Medium
Advisory: CVE-2019-15118
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-16
Source: https://osv.dev/vulnerability/CVE-2019-15118
Type: osv

## Details
check_input_term in sound/usb/mixer.c in the Linux kernel through 5.2.9 mishandles recursion, leading to kernel stack exhaustion.

## References
- https://usn.ubuntu.com/4162-2/
- https://usn.ubuntu.com/4163-1/
- https://www.debian.org/security/2019/dsa-4531
- https://usn.ubuntu.com/4147-1/
- https://usn.ubuntu.com/4162-1/
- https://seclists.org/bugtraq/2019/Sep/41
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://usn.ubuntu.com/4163-2/
- https://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound.git/commit/?id=19bce474c45be69a284ecee660aa12d8f1e88f18
- https://lore.kernel.org/lkml/20190815043554.16623-1-benquike%40gmail.com/
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://seclists.org/bugtraq/2019/Nov/11
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00000.html
