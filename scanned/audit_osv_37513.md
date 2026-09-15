# [H] Bluetooth: SMP: derive legacy responder STK authentication from MITM state

## Summary
Severity: High
Advisory: CVE-2026-31773
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31773
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: SMP: derive legacy responder STK authentication from MITM state

The legacy responder path in smp_random() currently labels the stored
STK as authenticated whenever pending_sec_level is BT_SECURITY_HIGH.
That reflects what the local service requested, not what the pairing
flow actually achieved.

For Just Works/Confirm legacy pairing, SMP_FLAG_MITM_AUTH stays clear
and the resulting STK should remain unauthenticated even if the local
side requested HIGH security. Use the established MITM state when
storing the responder STK so the key metadata matches the pairing result.

This also keeps the legacy path aligned with the Secure Connections code,
which already treats JUST_WORKS/JUST_CFM as unauthenticated.

## References
- https://git.kernel.org/stable/c/061ee71ac6b03c9f8432fe49538c3682bfcf4cf3
- https://git.kernel.org/stable/c/0afc846bd80073ffcd2b8040f2b2fafaea3d9f72
- https://git.kernel.org/stable/c/20756fec2f0108cb88e815941f1ffff88dc286fe
- https://git.kernel.org/stable/c/667f44f1392df6482483756458c48670e579e9ff
- https://git.kernel.org/stable/c/929db734d12db41ca5f95424db4612397f1bd4a7
- https://git.kernel.org/stable/c/9a38659a3d06080715691bd3139f9c4b61f688e3
- https://git.kernel.org/stable/c/9a6d0db176f082685e0b6149700c0baf3ce2aa8b
- https://git.kernel.org/stable/c/b1c6a8e554a39b222c0879a288ea98e338fc4d77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31773.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31773
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
