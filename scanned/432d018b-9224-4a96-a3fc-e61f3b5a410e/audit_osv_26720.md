# [H] scsi: ses: Fix possible desc_ptr out-of-bounds accesses

## Summary
Severity: High
Advisory: CVE-2023-53675
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53675
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ses: Fix possible desc_ptr out-of-bounds accesses

Sanitize possible desc_ptr out-of-bounds accesses in
ses_enclosure_data_process().

## References
- https://git.kernel.org/stable/c/414418abc19fa4ccf730d273061a426c07a061d6
- https://git.kernel.org/stable/c/4b8cae410472653a59e15af62c57c49b8e0a1201
- https://git.kernel.org/stable/c/584892fd29a41ef424a148118a3103b16b94fb8c
- https://git.kernel.org/stable/c/72021ae61a2bc6ca73cd593e255a10ed5f5dc5e7
- https://git.kernel.org/stable/c/79ec5dd5fb07ecaea2f978c2d7a9f2f3526e4d19
- https://git.kernel.org/stable/c/801ab13d50cf3d26170ee073ea8bb4eececb76ab
- https://git.kernel.org/stable/c/c315560e3ef77c1d822249f1743e647dc9c9912a
- https://git.kernel.org/stable/c/cffe09ca0555e235a42d6fa065e463c4b3d5b657
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53675.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53675
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
