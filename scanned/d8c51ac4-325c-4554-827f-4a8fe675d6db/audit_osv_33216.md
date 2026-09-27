# [H] mm/slub: avoid accessing metadata when pointer is invalid in object_err()

## Summary
Severity: High
Advisory: CVE-2025-39902
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39902
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.4.299, >=5.5.0 <5.10.243, >=5.11.0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/slub: avoid accessing metadata when pointer is invalid in object_err()

object_err() reports details of an object for further debugging, such as
the freelist pointer, redzone, etc. However, if the pointer is invalid,
attempting to access object metadata can lead to a crash since it does
not point to a valid object.

One known path to the crash is when alloc_consistency_checks()
determines the pointer to the allocated object is invalid because of a
freelist corruption, and calls object_err() to report it. The debug code
should report and handle the corruption gracefully and not crash in the
process.

In case the pointer is NULL or check_valid_pointer() returns false for
the pointer, only print the pointer value and skip accessing metadata.

## References
- https://git.kernel.org/stable/c/0ef7058b4dc6fcef622ac23b45225db57f17b83f
- https://git.kernel.org/stable/c/1f0797f17927b5cad0fb7eced422f9a7c30a3191
- https://git.kernel.org/stable/c/3baa1da473e6e50281324ff1d332d1a07a3bb02e
- https://git.kernel.org/stable/c/7e287256904ee796c9477e3ec92b07f236481ef3
- https://git.kernel.org/stable/c/872f2c34ff232af1e65ad2df86d61163c8ffad42
- https://git.kernel.org/stable/c/b4efccec8d06ceb10a7d34d7b1c449c569d53770
- https://git.kernel.org/stable/c/dda6ec365ab04067adae40ef17015db447e90736
- https://git.kernel.org/stable/c/f66012909e7bf383fcdc5850709ed5716073fdc4
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39902.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39902
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
