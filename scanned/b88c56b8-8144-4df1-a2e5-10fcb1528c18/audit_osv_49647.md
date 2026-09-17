# [H] CVE-2019-15117

## Summary
Severity: High
Advisory: CVE-2019-15117
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-16
Source: https://osv.dev/vulnerability/CVE-2019-15117
Type: osv

## Details
parse_audio_mixer_unit in sound/usb/mixer.c in the Linux kernel through 5.2.9 mishandles a short descriptor, leading to out-of-bounds memory access.

## References
- https://seclists.org/bugtraq/2019/Sep/41
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://support.f5.com/csp/article/K16449953?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- https://usn.ubuntu.com/4147-1/
- https://usn.ubuntu.com/4163-1/
- https://usn.ubuntu.com/4163-2/
- https://lists.debian.org/debian-lts-announce/2019/10/msg00000.html
- https://lore.kernel.org/lkml/20190814023625.21683-1-benquike%40gmail.com/
- https://seclists.org/bugtraq/2019/Nov/11
- https://usn.ubuntu.com/4162-1/
- https://usn.ubuntu.com/4162-2/
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://www.debian.org/security/2019/dsa-4531
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/tiwai/sound.git/commit/?id=daac07156b330b18eb5071aec4b3ddca1c377f2c
