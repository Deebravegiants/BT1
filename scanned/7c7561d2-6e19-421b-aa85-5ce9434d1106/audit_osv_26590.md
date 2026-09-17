# [H] cifs: prevent use-after-free by freeing the cfile later

## Summary
Severity: High
Advisory: CVE-2023-53377
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53377
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: prevent use-after-free by freeing the cfile later

In smb2_compound_op we have a possible use-after-free
which can cause hard to debug problems later on.

This was revealed during stress testing with KASAN enabled
kernel. Fixing it by moving the cfile free call to
a few lines below, after the usage.

## References
- https://git.kernel.org/stable/c/33f736187d08f6bc822117629f263b97d3df4165
- https://git.kernel.org/stable/c/4fe07d55a5461e66a55fbefb57f85ff0facea32b
- https://git.kernel.org/stable/c/b6353518ef8180816e863aa23b06456f395404d6
- https://git.kernel.org/stable/c/d017880782cf71f8820ee4a2002843893176501d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53377.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53377
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
