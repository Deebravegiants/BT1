# [M] octeontx2-pf: handle otx2_mbox_get_rsp errors in cn10k.c

## Summary
Severity: Medium
Advisory: CVE-2024-56726
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56726
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: handle otx2_mbox_get_rsp errors in cn10k.c

Add error pointer check after calling otx2_mbox_get_rsp().

## References
- https://git.kernel.org/stable/c/41f39f4c67253f802809310be6846ff408c3c758
- https://git.kernel.org/stable/c/54abcec092616a4d01195355eb5d6036fb8fe363
- https://git.kernel.org/stable/c/856ad633e11869729be698df2287ecfe6ec31f27
- https://git.kernel.org/stable/c/a374e7e79fbdd7574bd89344447b0d4b91ba9801
- https://git.kernel.org/stable/c/ac9183023b6a9c09467516abd8aab04f9a2f9564
- https://git.kernel.org/stable/c/c5a6c5af434671aea739a5a41c849819144f02c9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56726.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56726
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
