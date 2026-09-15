# [M] ALSA: usb-audio: Stop parsing channels bits when all channels are found.

## Summary
Severity: Medium
Advisory: CVE-2024-27436
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27436
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: Stop parsing channels bits when all channels are found.

If a usb audio device sets more bits than the amount of channels
it could write outside of the map array.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/22cad1b841a63635a38273b799b4791f202ade72
- https://git.kernel.org/stable/c/5cd466673b34bac369334f66cbe14bb77b7d7827
- https://git.kernel.org/stable/c/629af0d5fe94a35f498ba2c3f19bd78bfa591be6
- https://git.kernel.org/stable/c/6d5dc96b154be371df0d62ecb07efe400701ed8a
- https://git.kernel.org/stable/c/6d88b289fb0a8d055cb79d1c46a56aba7809d96d
- https://git.kernel.org/stable/c/7e2c1b0f6dd9abde9e60f0f9730026714468770f
- https://git.kernel.org/stable/c/9af1658ba293458ca6a13f70637b9654fa4be064
- https://git.kernel.org/stable/c/a39d51ff1f52cd0b6fe7d379ac93bd8b4237d1b7
- https://git.kernel.org/stable/c/c8a24fd281dcdf3c926413dafbafcf35cde517a9
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27436.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27436
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
