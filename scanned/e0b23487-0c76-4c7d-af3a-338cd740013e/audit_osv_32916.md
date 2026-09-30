# [H] Bluetooth: eir: Fix possible crashes on eir_create_adv_data

## Summary
Severity: High
Advisory: CVE-2025-38303
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38303
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.168, >=6.2.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: eir: Fix possible crashes on eir_create_adv_data

eir_create_adv_data may attempt to add EIR_FLAGS and EIR_TX_POWER
without checking if that would fit.

## References
- https://git.kernel.org/stable/c/2af40d795d3fb0ee5c074b7ac56ab22402aa6e4f
- https://git.kernel.org/stable/c/2d4588f55cc10fc228f3b46469dbfb3f0a8b13c8
- https://git.kernel.org/stable/c/47c03902269aff377f959dc3fd94a9733aa31d6e
- https://git.kernel.org/stable/c/b9db0c27e73b7c8a19384a44af527edfda74ff3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38303.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
