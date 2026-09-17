# [H] HID: wacom: stop hardware after post-start probe failures

## Summary
Severity: High
Advisory: CVE-2026-68091
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68091
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: wacom: stop hardware after post-start probe failures

wacom_parse_and_register() starts HID hardware before registering inputs
and initializing pad LEDs/remotes. Those later steps can fail, but their
error paths currently release Wacom resources without stopping the HID
hardware.

Route post-hid_hw_start() failures through hid_hw_stop() before
releasing driver resources.

This issue was identified during our ongoing static-analysis research while
reviewing kernel code.

## References
- https://git.kernel.org/stable/c/1a1ebdcb56ae58a0ee2c54dd15d75121e30424e3
- https://git.kernel.org/stable/c/3e6473a4f0596182acdda5219b4bebfbee76514f
- https://git.kernel.org/stable/c/416095e9a6037b4b39fcadd0d2bd77a8852211ec
- https://git.kernel.org/stable/c/46d8b8c85ae0589fb85746a64e8908160e52aac3
- https://git.kernel.org/stable/c/5a7ca028facf04921b2c1c2e4d1ee7f282510555
- https://git.kernel.org/stable/c/75eb2173b63ab41c24d80cd641af18f3c117a267
- https://git.kernel.org/stable/c/e2cc711a9df37f359159b21db56cea9c21f58a9c
- https://git.kernel.org/stable/c/ec2612b8ad9e642596db011dd8b6568ef1edeaa1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68091
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
