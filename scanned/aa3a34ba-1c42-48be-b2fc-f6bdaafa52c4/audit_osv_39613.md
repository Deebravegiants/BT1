# [C] lib/scatterlist: fix length calculations in extract_kvec_to_sg

## Summary
Severity: Critical
Advisory: CVE-2026-46289
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46289
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib/scatterlist: fix length calculations in extract_kvec_to_sg

Patch series "Fix bugs in extract_iter_to_sg()", v3.

Fix bugs in the kvec and user variants of extract_iter_to_sg.  This series
is growing due to useful remarks made by sashiko.dev.

The main bugs are:
- The length for an sglist entry when extracting from
  a kvec can exceed the number of bytes in the page. This
  is obviously not intended.
- When extracting a user buffer the sglist is temporarily
  used as a scratch buffer for extracted page pointers.
  If the sglist already contains some elements this scratch
  buffer could overlap with existing entries in the sglist.

The series adds test cases to the kunit_iov_iter test that demonstrate all
of these bugs.  Additionally, there is a memory leak fix for the test
itself.

The bugs were orignally introduced into kernel v6.3 where the function
lived in fs/netfs/iterator.c.  It was later moved to lib/scatterlist.c in
v6.5.  Thus the actual fix is only marked for backports to v6.5+.


This patch (of 5):

When extracting from a kvec to a scatterlist, do not cross page
boundaries.  The required length was already calculated but not used as
intended.

Adjust the copied length if the loop runs out of sglist entries without
extracting everything.

While there, return immediately from extract_iter_to_sg if there are no
sglist entries at all.

A subsequent commit will add kunit test cases that demonstrate that the
patch is necessary.

## References
- https://git.kernel.org/stable/c/07b7d66e65d9cfe6b9c2c34aa22cfcaac37a5c45
- https://git.kernel.org/stable/c/3f17500e86d730c76db638bb3ae52f9b5e496c76
- https://git.kernel.org/stable/c/8fbba6829057979149d1b37d65690c037f3ddf4d
- https://git.kernel.org/stable/c/9d38756d0a93b66163554219fa9c3365f40c4035
- https://git.kernel.org/stable/c/e5e22fc9963469e678c4f4bb38d26adcec107f1e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46289.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46289
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
