# [H] Bluetooth: hci_sock: Fix not validating setsockopt user input

## Summary
Severity: High
Advisory: CVE-2024-35963
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35963
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sock: Fix not validating setsockopt user input

Check user input length before copying data.

## References
- https://git.kernel.org/stable/c/0c18a64039aa3f1c16f208d197c65076da798137
- https://git.kernel.org/stable/c/50173882bb187e70e37bac01385b9b114019bee2
- https://git.kernel.org/stable/c/781f3a97a38a338bc893b6db7f9f9670bf1a9e37
- https://git.kernel.org/stable/c/b2186061d6043d6345a97100460363e990af0d46
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35963.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35963
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
