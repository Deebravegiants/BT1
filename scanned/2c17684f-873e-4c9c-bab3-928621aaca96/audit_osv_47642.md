# [H] CVE-2016-9794

## Summary
Severity: High
Advisory: CVE-2016-9794
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-9794
Type: osv

## Details
Race condition in the snd_pcm_period_elapsed function in sound/core/pcm_lib.c in the ALSA subsystem in the Linux kernel before 4.7 allows local users to cause a denial of service (use-after-free) or possibly have unspecified other impact via a crafted SNDRV_PCM_TRIGGER_START command.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00081.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00088.html
- http://www.securityfocus.com/bid/94654
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00091.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00075.html
- https://source.android.com/security/bulletin/2017-05-01
- https://patchwork.kernel.org/patch/8752621/
- https://bugzilla.redhat.com/show_bug.cgi?id=1401494
- http://www.openwall.com/lists/oss-security/2016/12/03/2
- https://github.com/torvalds/linux/commit/3aa02cb664c5fb1042958c8d1aa8c35055a2ebc4
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3aa02cb664c5fb1042958c8d1aa8c35055a2ebc4
