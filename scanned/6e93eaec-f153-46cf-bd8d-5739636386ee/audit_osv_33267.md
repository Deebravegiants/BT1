# [H] i40e: add validation for ring_len param

## Summary
Severity: High
Advisory: CVE-2025-39973
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39973
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: add validation for ring_len param

The `ring_len` parameter provided by the virtual function (VF)
is assigned directly to the hardware memory context (HMC) without
any validation.

To address this, introduce an upper boundary check for both Tx and Rx
queue lengths. The maximum number of descriptors supported by the
hardware is 8k-32.
Additionally, enforce alignment constraints: Tx rings must be a multiple
of 8, and Rx rings must be a multiple of 32.

## References
- https://git.kernel.org/stable/c/0543d40d6513cdf1c7882811086e59a6455dfe97
- https://git.kernel.org/stable/c/05fe81fb9db20464fa532a3835dc8300d68a2f84
- https://git.kernel.org/stable/c/45a7527cd7da4cdcf3b06b5c0cb1cae30b5a5985
- https://git.kernel.org/stable/c/55d225670def06b01af2e7a5e0446fbe946289e8
- https://git.kernel.org/stable/c/7d749e38dd2b7e8a80da2ca30c93e09de95bfcf9
- https://git.kernel.org/stable/c/afec12adab55d10708179a64d95d650741e60fe0
- https://git.kernel.org/stable/c/c0c83f4cd074b75cecef107bfc349be7d516c9c4
- https://git.kernel.org/stable/c/d3b0d3f8d11fa957171fbb186e53998361a88d4e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39973.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39973
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
