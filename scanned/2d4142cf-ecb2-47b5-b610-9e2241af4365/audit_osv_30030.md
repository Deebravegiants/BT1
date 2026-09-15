# [H] drm/xe/tracing: Fix a potential TP_printk UAF

## Summary
Severity: High
Advisory: CVE-2024-49570
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-49570
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/tracing: Fix a potential TP_printk UAF

The commit
afd2627f727b ("tracing: Check "%s" dereference via the field and not the TP_printk format")
exposes potential UAFs in the xe_bo_move trace event.

Fix those by avoiding dereferencing the
xe_mem_type_to_name[] array at TP_printk time.

Since some code refactoring has taken place, explicit backporting may
be needed for kernels older than 6.10.

## References
- https://git.kernel.org/stable/c/07089083a526ea19daa72a1edf9d6e209615b77c
- https://git.kernel.org/stable/c/62cd174616ae3bf8a6cf468718f1ae74e5a07727
- https://git.kernel.org/stable/c/c9402da34611e1039ecccba3c1481c4866f7ca64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49570.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
