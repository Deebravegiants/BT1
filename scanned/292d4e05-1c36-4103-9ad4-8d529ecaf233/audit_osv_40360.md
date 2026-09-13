# [H] bpf: Validate node_id in arena_alloc_pages()

## Summary
Severity: High
Advisory: CVE-2026-53031
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53031
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Validate node_id in arena_alloc_pages()

arena_alloc_pages() accepts a plain int node_id and forwards it through
the entire allocation chain without any bounds checking.

Validate node_id before passing it down the allocation chain in
arena_alloc_pages().

## References
- https://git.kernel.org/stable/c/2845989f2ebaf7848e4eccf9a779daf3156ea0a5
- https://git.kernel.org/stable/c/31d3b4b28e55835646d6829d60023f730dd34e85
- https://git.kernel.org/stable/c/e15900888c09480a4c632bc598f1c5bd39bed6d6
- https://git.kernel.org/stable/c/fb66e20130f95a93ffea1677252526a9e39170b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53031.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53031
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
