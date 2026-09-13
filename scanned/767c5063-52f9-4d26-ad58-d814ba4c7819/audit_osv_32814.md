# [H] espintcp: fix skb leaks

## Summary
Severity: High
Advisory: CVE-2025-38057
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38057
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.15.199, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

espintcp: fix skb leaks

A few error paths are missing a kfree_skb.

## References
- https://git.kernel.org/stable/c/05db2b850a2b8b17f3d1799f563ea1d550e05ed5
- https://git.kernel.org/stable/c/28756f22de48d25256ed89234b66b9037a3f0157
- https://git.kernel.org/stable/c/63c1f19a3be3169e51a5812d22a6d0c879414076
- https://git.kernel.org/stable/c/d8d79cf8c2b7475c22f9874eb844bcc80f858b13
- https://git.kernel.org/stable/c/e2e1f50fc5ebd2826c4e8c558dc65434382d0c0b
- https://git.kernel.org/stable/c/eb058693dfc93ed7a9c365adb899fedd648b9d9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38057.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38057
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
