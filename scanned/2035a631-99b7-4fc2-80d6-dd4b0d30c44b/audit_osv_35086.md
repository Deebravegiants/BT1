# [H] staging: rtl8723bs: fix stack buffer overflow in OnAssocReq IE parsing

## Summary
Severity: High
Advisory: CVE-2025-68255
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68255
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.62, >=6.13.0 <6.17.12, >=6.18.0 <6.18.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix stack buffer overflow in OnAssocReq IE parsing

The Supported Rates IE length from an incoming Association Request frame
was used directly as the memcpy() length when copying into a fixed-size
16-byte stack buffer (supportRate). A malicious station can advertise an
IE length larger than 16 bytes, causing a stack buffer overflow.

Clamp ie_len to the buffer size before copying the Supported Rates IE,
and correct the bounds check when merging Extended Supported Rates to
prevent a second potential overflow.

This prevents kernel stack corruption triggered by malformed association
requests.

## References
- https://git.kernel.org/stable/c/25411f5fcf5743131158f337c99c2bbf3f8477f5
- https://git.kernel.org/stable/c/34620eb602aa432f090b2b784ee5c5070fb16cf9
- https://git.kernel.org/stable/c/4445adedae770037078803d1ce41f9e88a1944b6
- https://git.kernel.org/stable/c/49b7806851f93fd342838c93f4f765e0cc5029b0
- https://git.kernel.org/stable/c/61871c83259a511980ec2664964cecc69005398b
- https://git.kernel.org/stable/c/6ef0e1c10455927867cac8f0ed6b49f328f8cf95
- https://git.kernel.org/stable/c/d129dc2a5d59b4d9cd2cc0b6eeb04df8461199f0
- https://git.kernel.org/stable/c/e841d8ea722315b781c4fc5bf4f7670fbca88875
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68255.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68255
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
