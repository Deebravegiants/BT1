# [H] greybus: gb-beagleplay: bound bootloader receive buffering

## Summary
Severity: High
Advisory: CVE-2026-46332
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46332
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

greybus: gb-beagleplay: bound bootloader receive buffering

cc1352_bootloader_rx() appends each serdev chunk into the fixed
rx_buffer before parsing bootloader packets. The helper can keep
leftover bytes between callbacks and may receive multiple packets in one
callback, so a single count value is not constrained by one packet
length.

Check that the incoming chunk fits in the remaining receive buffer space
before memcpy(). If it does not, drop the staged data and consume the
bytes instead of overflowing rx_buffer.

## References
- https://git.kernel.org/stable/c/0339a746ff7cd3f9d10f565e89c99dc93191e58d
- https://git.kernel.org/stable/c/1214bf28965ceaf584fb20d357731264dd2e10e1
- https://git.kernel.org/stable/c/663c2728a6d0f781044431111b53a27f71027e48
- https://git.kernel.org/stable/c/fb91d4e49fcbea0b5091394ac5b8f7d4124265c3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46332.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46332
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
