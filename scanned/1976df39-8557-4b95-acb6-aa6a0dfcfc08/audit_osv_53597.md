# [H] CVE-2023-0266

## Summary
Severity: High
Advisory: CVE-2023-0266
Aliases: A-265303544, PUB-A-265303544
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-30
Source: https://osv.dev/vulnerability/CVE-2023-0266
Type: osv

## Details
A use after free vulnerability exists in the ALSA PCM package in the Linux Kernel. SNDRV_CTL_IOCTL_ELEM_{READ|WRITE}32 is missing locks that can be used in a use-after-free that can result in a priviledge escalation to gain ring0 access from the system user. We recommend upgrading past commit 56b88b50565cd8b946a2d00b0c83927b7ebb055e

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-0266
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/stable-queue.git/tree/queue-5.10/alsa-pcm-move-rwsem-lock-inside-snd_ctl_elem_read-to-prevent-uaf.patch?id=72783cf35e6c55bca84c4bb7b776c58152856fd4
- https://github.com/torvalds/linux/commit/56b88b50565cd8b946a2d00b0c83927b7ebb055e
- https://github.com/torvalds/linux/commit/becf9e5d553c2389d857a3c178ce80fdb34a02e1
