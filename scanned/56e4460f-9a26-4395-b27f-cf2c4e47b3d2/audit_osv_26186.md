# [C] ksmbd: fix out of bounds in init_smb2_rsp_hdr()

## Summary
Severity: Critical
Advisory: CVE-2023-52441
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2023-52441
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.145, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix out of bounds in init_smb2_rsp_hdr()

If client send smb2 negotiate request and then send smb1 negotiate
request, init_smb2_rsp_hdr is called for smb1 negotiate request since
need_neg is set to false. This patch ignore smb1 packets after ->need_neg
is set to false.

## References
- https://git.kernel.org/stable/c/330d900620dfc9893011d725b3620cd2ee0bc2bc
- https://git.kernel.org/stable/c/536bb492d39bb6c080c92f31e8a55fe9934f452b
- https://git.kernel.org/stable/c/5c0df9d30c289d6b9d7d44e2a450de2f8e3cf40b
- https://git.kernel.org/stable/c/aa669ef229ae8dd779da9caa24e254964545895f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52441.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52441
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
