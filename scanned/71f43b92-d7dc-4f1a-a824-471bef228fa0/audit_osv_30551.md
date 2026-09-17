# [H] Bluetooth: hci_event: Align BR/EDR JUST_WORKS paring with LE

## Summary
Severity: High
Advisory: CVE-2024-53144
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-17
Source: https://osv.dev/vulnerability/CVE-2024-53144
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: Align BR/EDR JUST_WORKS paring with LE

This aligned BR/EDR JUST_WORKS method with LE which since 92516cd97fd4
("Bluetooth: Always request for user confirmation for Just Works")
always request user confirmation with confirm_hint set since the
likes of bluetoothd have dedicated policy around JUST_WORKS method
(e.g. main.conf:JustWorksRepairing).

CVE: CVE-2024-8805

## References
- https://git.kernel.org/stable/c/22b49d6e4f399a390c70f3034f5fbacbb9413858
- https://git.kernel.org/stable/c/5291ff856d2c5177b4fe9c18828312be30213193
- https://git.kernel.org/stable/c/830c03e58beb70b99349760f822e505ecb4eeb7e
- https://git.kernel.org/stable/c/ad7adfb95f64a761e4784381e47bee1a362eb30d
- https://git.kernel.org/stable/c/b25e11f978b63cb7857890edb3a698599cddb10e
- https://git.kernel.org/stable/c/baaa50c6f91ea5a9c7503af51f2bc50e6568b66b
- https://git.kernel.org/stable/c/d17c631ba04e960eb6f8728b10d585de20ac4f71
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53144.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53144
- https://www.zerodayinitiative.com/advisories/ZDI-24-1229/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
