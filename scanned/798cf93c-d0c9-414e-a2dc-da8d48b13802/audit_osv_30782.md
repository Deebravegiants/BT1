# [H] ALSA: caiaq: Use snd_card_free_when_closed() at disconnection

## Summary
Severity: High
Advisory: CVE-2024-56531
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56531
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: caiaq: Use snd_card_free_when_closed() at disconnection

The USB disconnect callback is supposed to be short and not too-long
waiting.  OTOH, the current code uses snd_card_free() at
disconnection, but this waits for the close of all used fds, hence it
can take long.  It eventually blocks the upper layer USB ioctls, which
may trigger a soft lockup.

An easy workaround is to replace snd_card_free() with
snd_card_free_when_closed().  This variant returns immediately while
the release of resources is done asynchronously by the card device
release at the last close.

This patch also splits the code to the disconnect and the free phases;
the former is called immediately at the USB disconnect callback while
the latter is called from the card destructor.

## References
- https://git.kernel.org/stable/c/237f3faf0177bdde728fa3106d730d806436aa4d
- https://git.kernel.org/stable/c/3993edf44d3df7b6e8c753eac6ac8783473fcbab
- https://git.kernel.org/stable/c/4507a8b9b30344c5ddd8219945f446d47e966a6d
- https://git.kernel.org/stable/c/4dd821dcbfcecf7af6a08370b0b217cde2818acf
- https://git.kernel.org/stable/c/a3f9314752dbb6f6aa1f0f2b4c58243bda800738
- https://git.kernel.org/stable/c/b04dcbb7f7b1908806b7dc22671cdbe78ff2b82c
- https://git.kernel.org/stable/c/cadf1d8e9ddcd74584ec961aeac14ac549b261d8
- https://git.kernel.org/stable/c/dd0de8cb708951cebf727aa045e8242ba651bb52
- https://git.kernel.org/stable/c/ebad462eec93b0f701dfe4de98990e7355283801
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56531.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56531
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
