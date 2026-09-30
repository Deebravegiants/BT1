# [M] ALSA: usx2y: Use snd_card_free_when_closed() at disconnection

## Summary
Severity: Medium
Advisory: CVE-2024-56533
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56533
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usx2y: Use snd_card_free_when_closed() at disconnection

The USB disconnect callback is supposed to be short and not too-long
waiting.  OTOH, the current code uses snd_card_free() at
disconnection, but this waits for the close of all used fds, hence it
can take long.  It eventually blocks the upper layer USB ioctls, which
may trigger a soft lockup.

An easy workaround is to replace snd_card_free() with
snd_card_free_when_closed().  This variant returns immediately while
the release of resources is done asynchronously by the card device
release at the last close.

## References
- https://git.kernel.org/stable/c/24fe9f7ca83ec9acf765339054951f5cd9ae5c5d
- https://git.kernel.org/stable/c/7bd8838c0ea886679a32834fdcacab296d072fbe
- https://git.kernel.org/stable/c/befcca1777525e37c659b4129d8ac7463b07ef67
- https://git.kernel.org/stable/c/dafb28f02be407e07a6f679e922a626592b481b0
- https://git.kernel.org/stable/c/e07605d855c4104d981653146a330ea48f6266ed
- https://git.kernel.org/stable/c/e869642a77a9b3b98b0ab2c8fec7af4385140909
- https://git.kernel.org/stable/c/ffbfc6c4330fc233698529656798bee44fea96f5
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56533.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56533
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
