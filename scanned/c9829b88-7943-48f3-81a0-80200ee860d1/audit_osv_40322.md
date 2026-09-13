# [H] virt: sev-guest: Do not use host-controlled page order in cleanup path

## Summary
Severity: High
Advisory: CVE-2026-52959
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52959
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

virt: sev-guest: Do not use host-controlled page order in cleanup path

When issuing an extended guest request (SVM_VMGEXIT_EXT_GUEST_REQUEST),
get_ext_report() allocates a buffer to retrieve a certificate blob from the
host, keeping track of its size in report_req->certs_len.

However, the host may return SNP_GUEST_VMM_ERR_INVALID_LEN, indicating
an invalid buffer size, as well as the expected length of such buffer.
get_ext_report() subsequently updates report_req->certs_len with the
host-controlled value, and cleans up the buffer by computing a page order
from such value. This is incorrect, as the host-provided length may not
match the page order of the original allocation, potentially resulting
in corruption in the page allocator.

Fix this by using alloc_pages_exact() instead, and reusing @npages to
compute the size passed to free_pages_exact(). For consistency, also
use @npages to compute the size when allocating the pages, even though
this last change has no functional effect.

## References
- https://git.kernel.org/stable/c/23e6a1ca04ae44806439a5a446e62e4d42e80bb4
- https://git.kernel.org/stable/c/3f6fb0211b39aaa1b841260681dd02ca6b693ed5
- https://git.kernel.org/stable/c/9e48b4f813d2c3db75d522aa82ab705ce04b7e2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52959.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52959
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
