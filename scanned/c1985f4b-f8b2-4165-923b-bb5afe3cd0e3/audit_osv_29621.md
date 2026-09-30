# [C] atm: idt77252: prevent use after free in dequeue_rx()

## Summary
Severity: Critical
Advisory: CVE-2024-44998
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44998
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.321, >=4.20.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

atm: idt77252: prevent use after free in dequeue_rx()

We can't dereference "skb" after calling vcc->push() because the skb
is released.

## References
- https://git.kernel.org/stable/c/09e086a5f72ea27c758b3f3b419a69000c32adc1
- https://git.kernel.org/stable/c/1cece837e387c039225f19028df255df87a97c0d
- https://git.kernel.org/stable/c/24cf390a5426aac9255205e9533cdd7b4235d518
- https://git.kernel.org/stable/c/379a6a326514a3e2f71b674091dfb0e0e7522b55
- https://git.kernel.org/stable/c/628ea82190a678a56d2ec38cda3addf3b3a6248d
- https://git.kernel.org/stable/c/91b4850e7165a4b7180ef1e227733bcb41ccdf10
- https://git.kernel.org/stable/c/a9a18e8f770c9b0703dab93580d0b02e199a4c79
- https://git.kernel.org/stable/c/ef23c18ab88e33ce000d06a5c6aad0620f219bfd
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44998.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
