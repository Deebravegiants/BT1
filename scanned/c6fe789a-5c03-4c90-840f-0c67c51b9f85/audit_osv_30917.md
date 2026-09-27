# [M] octeontx2-pf: handle otx2_mbox_get_rsp errors in otx2_dcbnl.c

## Summary
Severity: Medium
Advisory: CVE-2024-56725
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56725
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: handle otx2_mbox_get_rsp errors in otx2_dcbnl.c

Add error pointer check after calling otx2_mbox_get_rsp().

## References
- https://git.kernel.org/stable/c/54e8b501b3ea9371e4a9aa639c75b681fa5680f0
- https://git.kernel.org/stable/c/69297b0d3369488af259e3a7cf53d69157938ea1
- https://git.kernel.org/stable/c/6ee6cf42dc5230425cfce1ffefa5a8d8a99e6fce
- https://git.kernel.org/stable/c/b94052830e3cd3be7141789a5ce6e62cf9f620a4
- https://git.kernel.org/stable/c/b99db02209ca4c2e2f53b82049ea3cbc82b54895
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56725.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56725
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
