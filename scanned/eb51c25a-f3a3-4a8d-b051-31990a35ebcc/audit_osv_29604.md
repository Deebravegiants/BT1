# [H] ALSA: line6: Fix racy access to midibuf

## Summary
Severity: High
Advisory: CVE-2024-44954
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44954
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.105, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: line6: Fix racy access to midibuf

There can be concurrent accesses to line6 midibuf from both the URB
completion callback and the rawmidi API access.  This could be a cause
of KMSAN warning triggered by syzkaller below (so put as reported-by
here).

This patch protects the midibuf call of the former code path with a
spinlock for avoiding the possible races.

## References
- https://git.kernel.org/stable/c/15b7a03205b31bc5623378c190d22b7ff60026f1
- https://git.kernel.org/stable/c/40f3d5cb0e0cbf7fa697913a27d5d361373bdcf5
- https://git.kernel.org/stable/c/51d87f11dd199bbc6a85982b088ff27bde53b48a
- https://git.kernel.org/stable/c/535df7f896a568a8a1564114eaea49d002cb1747
- https://git.kernel.org/stable/c/643293b68fbb6c03f5e907736498da17d43f0d81
- https://git.kernel.org/stable/c/a54da4b787dcac60b598da69c9c0072812b8282d
- https://git.kernel.org/stable/c/c80f454a805443c274394b1db0d1ebf477abd94e
- https://git.kernel.org/stable/c/e7e7d2b180d8f297cea6db43ea72402fd33e1a29
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44954.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44954
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
