# [H] net: lan743x: Modify the EEPROM and OTP size for PCI1xxxx devices

## Summary
Severity: High
Advisory: CVE-2025-38422
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38422
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: lan743x: Modify the EEPROM and OTP size for PCI1xxxx devices

Maximum OTP and EEPROM size for hearthstone PCI1xxxx devices are 8 Kb
and 64 Kb respectively. Adjust max size definitions and return correct
EEPROM length based on device. Also prevent out-of-bound read/write.

## References
- https://git.kernel.org/stable/c/088279ff18cdc437d6fac5890e0c52c624f78a5b
- https://git.kernel.org/stable/c/3b9935586a9b54d2da27901b830d3cf46ad66a1e
- https://git.kernel.org/stable/c/51318d644c993b3f7a60b8616a6a5adc1e967cd2
- https://git.kernel.org/stable/c/6b4201d74d0a49af2123abf2c9d142e59566714b
- https://git.kernel.org/stable/c/9c41d2a2aa3817946eb613522200cab55513ddaa
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38422.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38422
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
