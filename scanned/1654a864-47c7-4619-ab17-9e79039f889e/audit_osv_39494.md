# [H] bpf: Fix a potential use-after-free of BTF object

## Summary
Severity: High
Advisory: CVE-2026-45951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45951
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix a potential use-after-free of BTF object

Refcounting in the check_pseudo_btf_id() function is incorrect:
the __check_pseudo_btf_id() function might get called with a zero
refcounted btf. Fix this, and patch related code accordingly.

v3: rephrase a comment (AI)
v2: fix a refcount leak introduced in v1 (AI)

## References
- https://git.kernel.org/stable/c/9ff46ffeecdb1802d6e26183177935b948a12e7f
- https://git.kernel.org/stable/c/ccd2d799ed4467c07f5ee18c2f5c59bcc990822c
- https://git.kernel.org/stable/c/eac65c272f3b49021a843cba5107d63627395e0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45951.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
