# [H] wireguard: allowedips: avoid unaligned 64-bit memory accesses

## Summary
Severity: High
Advisory: CVE-2024-42247
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42247
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wireguard: allowedips: avoid unaligned 64-bit memory accesses

On the parisc platform, the kernel issues kernel warnings because
swap_endian() tries to load a 128-bit IPv6 address from an unaligned
memory location:

 Kernel: unaligned access to 0x55f4688c in wg_allowedips_insert_v6+0x2c/0x80 [wireguard] (iir 0xf3010df)
 Kernel: unaligned access to 0x55f46884 in wg_allowedips_insert_v6+0x38/0x80 [wireguard] (iir 0xf2010dc)

Avoid such unaligned memory accesses by instead using the
get_unaligned_be64() helper macro.

[Jason: replace src[8] in original patch with src+8]

## References
- https://git.kernel.org/stable/c/217978a29c6ceca76d3c640bf94bdf50c268d801
- https://git.kernel.org/stable/c/2fb34bf76431e831f9863cd59adc0bd1f67b0fbf
- https://git.kernel.org/stable/c/6638a203abad35fa636d59ac47bdbc4bc100fd74
- https://git.kernel.org/stable/c/948f991c62a4018fb81d85804eeab3029c6209f8
- https://git.kernel.org/stable/c/ae630de24efb123d7199a43256396d7758f4cb75
- https://git.kernel.org/stable/c/b4764f0ad3d68de8a0b847c05f427afb86dd54e6
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42247.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42247
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
