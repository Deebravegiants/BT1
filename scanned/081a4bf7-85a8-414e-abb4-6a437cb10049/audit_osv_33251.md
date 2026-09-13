# [H] wifi: wilc1000: avoid buffer overflow in WID string configuration

## Summary
Severity: High
Advisory: CVE-2025-39952
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39952
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wilc1000: avoid buffer overflow in WID string configuration

Fix the following copy overflow warning identified by Smatch checker.

 drivers/net/wireless/microchip/wilc1000/wlan_cfg.c:184 wilc_wlan_parse_response_frame()
        error: '__memcpy()' 'cfg->s[i]->str' copy overflow (512 vs 65537)

This patch introduces size check before accessing the memory buffer.
The checks are base on the WID type of received data from the firmware.
For WID string configuration, the size limit is determined by individual
element size in 'struct wilc_cfg_str_vals' that is maintained in 'len' field
of 'struct wilc_cfg_str'.

## References
- https://git.kernel.org/stable/c/2203ef417044b10a8563ade6a17c74183745d72e
- https://git.kernel.org/stable/c/6085291a1a5865d4ad70f0e5812d524ebd5d1711
- https://git.kernel.org/stable/c/ae50f8562306a7ea1cf3c9722f97ee244f974729
- https://git.kernel.org/stable/c/fe9e4d0c39311d0f97b024147a0d155333f388b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39952.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39952
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
