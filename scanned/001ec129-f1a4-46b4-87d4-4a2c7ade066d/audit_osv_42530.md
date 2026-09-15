# [C] ksmbd: pin conn during async oplock break notification

## Summary
Severity: Critical
Advisory: CVE-2026-68381
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68381
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.14.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: pin conn during async oplock break notification

smb2_oplock_break_noti() and smb2_lease_break_noti() store a ksmbd_conn
pointer in an async ksmbd_work and then queue that work on ksmbd-io.  The
work only increments conn->r_count, which prevents teardown from passing
the pending-request wait after the increment, but it does not pin the
struct ksmbd_conn object.

If connection teardown races with an oplock break notification, the last
conn reference can be dropped before the queued worker finishes.  The
worker then uses the freed conn in ksmbd_conn_write() and
ksmbd_conn_r_count_dec().

Take a real conn reference when publishing the conn pointer to the async
work item, and drop it after the notification work has decremented
r_count.  Apply the same lifetime rule to lease break notification, which
uses the same work->conn pattern.

## References
- https://git.kernel.org/stable/c/0f72fc9659d7f585460d43c158055df5afdcffb6
- https://git.kernel.org/stable/c/14062c74e5b25c27edcff7a2fe0dc701c930b372
- https://git.kernel.org/stable/c/6ecb252efa0b413ac3d9979fb4eec247f8fc1258
- https://git.kernel.org/stable/c/793e1c7041b93af96ff87e678329bc16aee7ba88
- https://git.kernel.org/stable/c/aa5d8f3f96aa11a4a54ce993c11ce8af11c546f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68381.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68381
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
