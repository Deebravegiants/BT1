# [M] media: usbtv: Remove useless locks in usbtv_video_free()

## Summary
Severity: Medium
Advisory: CVE-2024-27072
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27072
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: usbtv: Remove useless locks in usbtv_video_free()

Remove locks calls in usbtv_video_free() because
are useless and may led to a deadlock as reported here:
https://syzkaller.appspot.com/x/bisect.txt?x=166dc872180000
Also remove usbtv_stop() call since it will be called when
unregistering the device.

Before 'c838530d230b' this issue would only be noticed if you
disconnect while streaming and now it is noticeable even when
disconnecting while not streaming.


[hverkuil: fix minor spelling mistake in log message]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/3e7d82ebb86e94643bdb30b0b5b077ed27dce1c2
- https://git.kernel.org/stable/c/4ec4641df57cbdfdc51bb4959afcdbcf5003ddb9
- https://git.kernel.org/stable/c/65e6a2773d655172143cc0b927cdc89549842895
- https://git.kernel.org/stable/c/bdd82c47b22a8befd617b723098b2a41b77373c7
- https://git.kernel.org/stable/c/d5ed208d04acf06781d63d30f9fa991e8d609ebd
- https://git.kernel.org/stable/c/dea46e246ef0f98d89d59a4229157cd9ffb636bf
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27072.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
