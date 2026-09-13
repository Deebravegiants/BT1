# [H] CVE-2018-10902

## Summary
Severity: High
Advisory: CVE-2018-10902
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-10902
Type: osv

## Details
It was found that the raw midi kernel driver does not protect against concurrent access which leads to a double realloc (double free) in snd_rawmidi_input_params() and snd_rawmidi_output_status() which are part of snd_rawmidi_ioctl() handler in rawmidi.c file. A malicious local attacker could possibly use this for privilege escalation.

## References
- https://usn.ubuntu.com/3849-2/
- https://access.redhat.com/errata/RHSA-2018:3096
- https://access.redhat.com/errata/RHSA-2019:0415
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3847-1/
- https://usn.ubuntu.com/3847-2/
- https://www.debian.org/security/2018/dsa-4308
- https://access.redhat.com/errata/RHSA-2019:0641
- https://access.redhat.com/errata/RHSA-2019:3967
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3847-3/
- https://usn.ubuntu.com/3849-1/
- http://www.securityfocus.com/bid/105119
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2019:3217
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10902
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=39675f7a7c7e7702f7d5341f1e0d01db746543a0
- http://www.securitytracker.com/id/1041529
