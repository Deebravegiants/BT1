# [H] ksmbd: Fix UAF in __close_file_table_ids

## Summary
Severity: High
Advisory: CVE-2025-37952
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37952
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: Fix UAF in __close_file_table_ids

A use-after-free is possible if one thread destroys the file
via __ksmbd_close_fd while another thread holds a reference to
it. The existing checks on fp->refcount are not sufficient to
prevent this.

The fix takes ft->lock around the section which removes the
file from the file table. This prevents two threads acquiring the
same file pointer via __close_file_table_ids, as well as the other
functions which retrieve a file from the IDR and which already use
this same lock.

## References
- https://git.kernel.org/stable/c/16727e442568a46d9cca69fe2595896de86e120d
- https://git.kernel.org/stable/c/36991c1ccde2d5a521577c448ffe07fcccfe104d
- https://git.kernel.org/stable/c/9e9841e232b51171ddf3bc4ee517d5d28dc8cad6
- https://git.kernel.org/stable/c/fec1f9e9a650e8e7011330a085c77e7bf2a08ea9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37952.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37952
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
