# [H] dpaa2-switch: add bounds check for if_id in IRQ handler

## Summary
Severity: High
Advisory: CVE-2026-23180
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23180
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dpaa2-switch: add bounds check for if_id in IRQ handler

The IRQ handler extracts if_id from the upper 16 bits of the hardware
status register and uses it to index into ethsw->ports[] without
validation. Since if_id can be any 16-bit value (0-65535) but the ports
array is only allocated with sw_attr.num_ifs elements, this can lead to
an out-of-bounds read potentially.

Add a bounds check before accessing the array, consistent with the
existing validation in dpaa2_switch_rx().

## References
- https://git.kernel.org/stable/c/1b381a638e1851d8cfdfe08ed9cdbec5295b18c9
- https://git.kernel.org/stable/c/2447edc367800ba914acf7ddd5d250416b45fb31
- https://git.kernel.org/stable/c/31a7a0bbeb006bac2d9c81a2874825025214b6d8
- https://git.kernel.org/stable/c/34b56c16efd61325d80bf1d780d0e176be662f59
- https://git.kernel.org/stable/c/77611cab5bdfff7a070ae574bbfba20a1de99d1b
- https://git.kernel.org/stable/c/f89e33c9c37f0001b730e23b3b05ab7b1ecface2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23180.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23180
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
