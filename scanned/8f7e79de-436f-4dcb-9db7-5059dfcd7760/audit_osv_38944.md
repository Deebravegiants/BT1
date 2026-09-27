# [H] Bluetooth: L2CAP: Fix missing key size check for L2CAP_LE_CONN_REQ

## Summary
Severity: High
Advisory: CVE-2026-43134
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43134
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Fix missing key size check for L2CAP_LE_CONN_REQ

This adds a check for encryption key size upon receiving
L2CAP_LE_CONN_REQ which is required by L2CAP/LE/CFC/BV-15-C which
expects L2CAP_CR_LE_BAD_KEY_SIZE.

## References
- https://git.kernel.org/stable/c/138d7eca445ef37a0333425d269ee59900ca1104
- https://git.kernel.org/stable/c/335071c0c3637064ec250481f589075db44fe4e6
- https://git.kernel.org/stable/c/481ea39b342c347b6ac029f3d418486280be4e45
- https://git.kernel.org/stable/c/8dd43f9a9323f9c01bc8246da8d81a4c783c9e97
- https://git.kernel.org/stable/c/9118601ff90b79e8df3c0c98f48ae00c1b02ecef
- https://git.kernel.org/stable/c/96581749c7c14fbec32c35728520867929600041
- https://git.kernel.org/stable/c/ec91078e132179b04e0c3906b599816c056ceaad
- https://git.kernel.org/stable/c/fa6ad76fa8623c0a50d529cd5726fa5d819a3be4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43134.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43134
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
