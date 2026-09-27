# [M] media: cx24116: prevent overflows on SNR calculus

## Summary
Severity: Medium
Advisory: CVE-2024-50290
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50290
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: cx24116: prevent overflows on SNR calculus

as reported by Coverity, if reading SNR registers fail, a negative
number will be returned, causing an underflow when reading SNR
registers.

Prevent that.

## References
- https://git.kernel.org/stable/c/127b9076baeadd734b18ddc8f2cd93b47d5a3ea3
- https://git.kernel.org/stable/c/3a1ed994d9454132354b860321414955da289929
- https://git.kernel.org/stable/c/576a307a7650bd544fbb24df801b9b7863b85e2f
- https://git.kernel.org/stable/c/828047c70f4716fde4b1316f7b610e97a4e83824
- https://git.kernel.org/stable/c/83c152b55d88cbf6fc4685941fcb31333986774d
- https://git.kernel.org/stable/c/cad97ca8cfd43a78a19b59949f33e3563d369247
- https://git.kernel.org/stable/c/f2b4f277c41db8d548f38f1dd091bbdf6a5acb07
- https://git.kernel.org/stable/c/fbefe31e4598cdb0889eee2e74c995b2212efb08
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50290.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50290
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
