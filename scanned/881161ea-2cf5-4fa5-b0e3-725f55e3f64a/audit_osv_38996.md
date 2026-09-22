# [H] octeontx2-af: Workaround SQM/PSE stalls by disabling sticky

## Summary
Severity: High
Advisory: CVE-2026-43296
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43296
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: Workaround SQM/PSE stalls by disabling sticky

NIX SQ manager sticky mode is known to cause stalls when multiple SQs
share an SMQ and transmit concurrently. Additionally, PSE may deadlock
on transitions between sticky and non-sticky transmissions. There is
also a credit drop issue observed when certain condition clocks are
gated.

work around these hardware errata by:
- Disabling SQM sticky operation:
  - Clear TM6 (bit 15)
  - Clear TM11 (bit 14)
- Disabling sticky → non-sticky transition path that can deadlock PSE:
  - Clear TM5 (bit 23)
- Preventing credit drops by keeping the control-flow clock enabled:
  - Set TM9 (bit 21)

These changes are applied via NIX_AF_SQM_DBG_CTL_STATUS. With this
configuration the SQM/PSE maintain forward progress under load without
credit loss, at the cost of disabling sticky optimizations.

## References
- https://git.kernel.org/stable/c/36cc5a5e0178d5fb79e04173b8aa623b0108819a
- https://git.kernel.org/stable/c/70e9a5760abfb6338d63994d4de6b0778ec795d6
- https://git.kernel.org/stable/c/8052d0587fb14b85539c3a14a226586c0c3d6b4c
- https://git.kernel.org/stable/c/9a3fd301329474f449e75f86d8a4f6b9c603fd6c
- https://git.kernel.org/stable/c/b7eba260a34e854e2487b8363c11976f082df00d
- https://git.kernel.org/stable/c/cec2ceb35ce7bc874c43812bb39200d6cf691b87
- https://git.kernel.org/stable/c/d0b3c8a80336029d9356f429151eb27922d80a3c
- https://git.kernel.org/stable/c/d9b549b6951ba178ec14339a031cae65f4e43fe1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43296.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
