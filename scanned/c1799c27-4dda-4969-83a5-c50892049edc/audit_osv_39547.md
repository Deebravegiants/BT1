# [C] libceph: Fix slab-out-of-bounds access in auth message processing

## Summary
Severity: Critical
Advisory: CVE-2026-46119
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46119
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: Fix slab-out-of-bounds access in auth message processing

If a (potentially corrupted) message of type CEPH_MSG_AUTH_REPLY
contains a positive value in its result field, it is treated as an
error code by ceph_handle_auth_reply() and returned to
handle_auth_reply(). Thereafter, an attempt is made to send the
preallocated message of type CEPH_MSG_AUTH, where the returned value is
interpreted as the size of the front segment to send. If the result
value in the message is greater than the size of the memory buffer
allocated for the front segment, an out-of-bounds access occurs, and
the content of the memory region beyond this buffer is sent out.

This patch fixes the issue by treating only negative values in the
result field as errors. Positive values are therefore treated as success
in the same way as a zero value. Additionally, a BUG_ON is added to
__send_prepared_auth_request() comparing the len parameter to
front_alloc_len to prevent sending the message if it exceeds the bounds
of the allocation and to make it easier to catch any logic flaws leading
to this.

## References
- https://git.kernel.org/stable/c/1c439de70b1c3eb3c6bffa8245c16b9fc318f114
- https://git.kernel.org/stable/c/2ae0afd98432536562fa8261538ae795446f0589
- https://git.kernel.org/stable/c/38fdf04c602d52c42c67fc1617211492753b7e8b
- https://git.kernel.org/stable/c/408e85ee708b6aa03eeb0220ffa0915f4d407181
- https://git.kernel.org/stable/c/8517b6c8d2c759918ba0058cb6c7e14d59643202
- https://git.kernel.org/stable/c/b7df9fbd4869fdfe09a3f501ffd228486521e062
- https://git.kernel.org/stable/c/c2374b92c729d0388a538b3cde7b3e3b5e55ef39
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46119.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46119
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
