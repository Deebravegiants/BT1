# [H] ovl: Use "buf" flexible array for memcpy() destination

## Summary
Severity: High
Advisory: CVE-2022-49743
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49743
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.248, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovl: Use "buf" flexible array for memcpy() destination

The "buf" flexible array needs to be the memcpy() destination to avoid
false positive run-time warning from the recent FORTIFY_SOURCE
hardening:

  memcpy: detected field-spanning write (size 93) of single field "&fh->fb"
  at fs/overlayfs/export.c:799 (size 21)

## References
- https://git.kernel.org/stable/c/012cdef22000f3104e4fa8224ad29fde509b8caf
- https://git.kernel.org/stable/c/07a96977b2f462337a9121302de64277b8747ab1
- https://git.kernel.org/stable/c/a77141a06367825d639ac51b04703d551163e36c
- https://git.kernel.org/stable/c/cf8aa9bf97cadf85745506c6a3e244b22c268d63
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49743.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49743
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
