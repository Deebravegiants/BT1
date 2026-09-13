# [H] bpf: Fix a potential use-after-free in bpf_link_free()

## Summary
Severity: High
Advisory: CVE-2024-40909
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40909
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix a potential use-after-free in bpf_link_free()

After commit 1a80dbcb2dba, bpf_link can be freed by
link->ops->dealloc_deferred, but the code still tests and uses
link->ops->dealloc afterward, which leads to a use-after-free as
reported by syzbot. Actually, one of them should be sufficient, so
just call one of them instead of both. Also add a WARN_ON() in case
of any problematic implementation.

## References
- https://git.kernel.org/stable/c/2884dc7d08d98a89d8d65121524bb7533183a63a
- https://git.kernel.org/stable/c/91cff53136daeff50816b0baeafd38a6976f6209
- https://git.kernel.org/stable/c/fa97b8fed9896f1e89cb657513e483a152d4c382
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40909.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
