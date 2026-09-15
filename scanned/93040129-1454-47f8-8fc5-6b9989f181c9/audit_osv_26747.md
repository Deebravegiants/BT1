# [C] virt/coco/sev-guest: Double-buffer messages

## Summary
Severity: Critical
Advisory: CVE-2023-53769
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2023-53769
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

virt/coco/sev-guest: Double-buffer messages

The encryption algorithms read and write directly to shared unencrypted
memory, which may leak information as well as permit the host to tamper
with the message integrity. Instead, copy whole messages in or out as
needed before doing any computation on them.

## References
- https://git.kernel.org/stable/c/4b69c63f716cfda38e1210e65b68f67f6cee2ddf
- https://git.kernel.org/stable/c/577a64725bfd77645986168e953d405067ee565b
- https://git.kernel.org/stable/c/965006103a14703cc42043bbf9b5e0cdf7a468ad
- https://git.kernel.org/stable/c/c27dafc4aa50a29ec927b3aa84ac7b430071f682
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53769.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53769
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
