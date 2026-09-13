# [H] usb: gadget: f_tcm: Don't free command immediately

## Summary
Severity: High
Advisory: CVE-2024-58055
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58055
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: f_tcm: Don't free command immediately

Don't prematurely free the command. Wait for the status completion of
the sense status. It can be freed then. Otherwise we will double-free
the command.

## References
- https://git.kernel.org/stable/c/16907219ad6763f401700e1b57b2da4f3e07f047
- https://git.kernel.org/stable/c/38229c35a6d7875697dfb293356407330cfcd23e
- https://git.kernel.org/stable/c/7cb72dc08ed8da60fd6d1f6adf13bf0e6ee0f694
- https://git.kernel.org/stable/c/929b69810eec132b284ffd19047a85d961df9e4d
- https://git.kernel.org/stable/c/bbb7f49839b57d66ccaf7b5752d9b63d3031dd0a
- https://git.kernel.org/stable/c/c225d006a31949d673e646d585d9569bc28feeb9
- https://git.kernel.org/stable/c/e6693595bd1b55af62d057a4136a89d5c2ddf0e9
- https://git.kernel.org/stable/c/f0c33e7d387ccbb6870e73a43c558fefede06614
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58055.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58055
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
