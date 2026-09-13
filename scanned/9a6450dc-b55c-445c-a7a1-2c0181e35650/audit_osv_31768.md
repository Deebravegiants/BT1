# [H] usbnet: ipheth: fix possible overflow in DPE length check

## Summary
Severity: High
Advisory: CVE-2025-21743
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21743
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

usbnet: ipheth: fix possible overflow in DPE length check

Originally, it was possible for the DPE length check to overflow if
wDatagramIndex + wDatagramLength > U16_MAX. This could lead to an OoB
read.

Move the wDatagramIndex term to the other side of the inequality.

An existing condition ensures that wDatagramIndex < urb->actual_length.

## References
- https://git.kernel.org/stable/c/18bf6f5cce3172cb303c3f0551aa9443d5ed74f8
- https://git.kernel.org/stable/c/c219427ed296f94bb4b91d08626776dc7719ee27
- https://git.kernel.org/stable/c/d677e7dd59ad6837496f5a02d8e5d39824278dfd
- https://git.kernel.org/stable/c/d824a964185910e317287f034c0a439c08b4fe49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21743.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21743
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
