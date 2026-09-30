# [H] cachefiles: fix incorrect dentry refcount in cachefiles_cull()

## Summary
Severity: High
Advisory: CVE-2026-43106
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43106
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

cachefiles: fix incorrect dentry refcount in cachefiles_cull()

The patch mentioned below changed cachefiles_bury_object() to expect 2
references to the 'rep' dentry.  Three of the callers were changed to
use start_removing_dentry() which takes an extra reference so in those
cases the call gets the expected references.

However there is another call to cachefiles_bury_object() in
cachefiles_cull() which did not need to be changed to use
start_removing_dentry() and so was not properly considered.
It still passed the dentry with just one reference so the net result is
that a reference is lost.

To meet the expectations of cachefiles_bury_object(), cachefiles_cull()
must take an extra reference before the call.  It will be dropped by
cachefiles_bury_object().

## References
- https://git.kernel.org/stable/c/1635c2acdde86c4f555b627aec873c8677c421ed
- https://git.kernel.org/stable/c/6577df7dc7a7de128442b6192c7a32195c923480
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43106.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43106
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
