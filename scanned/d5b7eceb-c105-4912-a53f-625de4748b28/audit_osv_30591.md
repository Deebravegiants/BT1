# [H] ALSA: usb-audio: Fix potential out-of-bound accesses for Extigy and Mbox devices

## Summary
Severity: High
Advisory: CVE-2024-53197
Aliases: A-382243530, ASB-A-382243530
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53197
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: Fix potential out-of-bound accesses for Extigy and Mbox devices

A bogus device can provide a bNumConfigurations value that exceeds the
initial value used in usb_get_configuration for allocating dev->config.

This can lead to out-of-bounds accesses later, e.g. in
usb_destroy_configuration.

## References
- https://git.kernel.org/stable/c/0b4ea4bfe16566b84645ded1403756a2dc4e0f19
- https://git.kernel.org/stable/c/379d3b9799d9da953391e973b934764f01e03960
- https://git.kernel.org/stable/c/62dc01c83fa71e10446ee4c31e0e3d5d1291e865
- https://git.kernel.org/stable/c/920a369a9f014f10ec282fd298d0666129379f1b
- https://git.kernel.org/stable/c/9887d859cd60727432a01564e8f91302d361b72b
- https://git.kernel.org/stable/c/9b8460a2a7ce478e0b625af7c56d444dc24190f7
- https://git.kernel.org/stable/c/b521b53ac6eb04e41c03f46f7fe452e4d8e9bcca
- https://git.kernel.org/stable/c/b8f8b81dabe52b413fe9e062e8a852c48dd0680d
- https://git.kernel.org/stable/c/b909df18ce2a998afef81d58bbd1a05dc0788c40
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-53197
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53197.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53197
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
