# [H] Revert "drm/xe: Skip exec queue schedule toggle if queue is idle during suspend"

## Summary
Severity: High
Advisory: CVE-2026-53201
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53201
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "drm/xe: Skip exec queue schedule toggle if queue is idle during suspend"

This reverts commit 8533051ce92015e9cc6f75e0d52119b9d91610b6.

The idle-skip optimization bypasses GuC suspend, so the GPU may not
perform the context switch that flushes TLB entries for invalidated
userptr VMAs. In LR/preempt-fence VM mode, this can lead to missed TLB
invalidation and page faults during userptr invalidation tests.

Restore unconditional schedule toggling on suspend so the context-switch
TLB flush is always performed.

This optimization will be reintroduced with a fix that does not skip
suspend in LR/preempt-fence VM mode.

(cherry picked from commit 6a1e7934d9a6cf46aecae00a99c2603d1295e170)

## References
- https://git.kernel.org/stable/c/b69b715f48ac7e802c89ed5924795c5b055da91e
- https://git.kernel.org/stable/c/fa7c84726dc217ce0c183926ef9411636c7a2213
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53201.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
