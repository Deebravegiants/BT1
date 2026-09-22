# [H] drm/xe/ct: prevent UAF in send_recv()

## Summary
Severity: High
Advisory: CVE-2024-50030
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50030
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/ct: prevent UAF in send_recv()

Ensure we serialize with completion side to prevent UAF with fence going
out of scope on the stack, since we have no clue if it will fire after
the timeout before we can erase from the xa. Also we have some dependent
loads and stores for which we need the correct ordering, and we lack the
needed barriers. Fix this by grabbing the ct->lock after the wait, which
is also held by the completion side.

v2 (Badal):
 - Also print done after acquiring the lock and seeing timeout.

(cherry picked from commit 52789ce35c55ccd30c4b67b9cc5b2af55e0122ea)

## References
- https://git.kernel.org/stable/c/8ed7dd4c55e4fb21531a9645aeb66a30eaf43a46
- https://git.kernel.org/stable/c/db7f92af626178ba59dbbcdd5dee9ec24a987a88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50030.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
