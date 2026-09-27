# [H] rust_binder: check ownership before using vma

## Summary
Severity: High
Advisory: CVE-2026-43434
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43434
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

rust_binder: check ownership before using vma

When installing missing pages (or zapping them), Rust Binder will look
up the vma in the mm by address, and then call vm_insert_page (or
zap_page_range_single). However, if the vma is closed and replaced with
a different vma at the same address, this can lead to Rust Binder
installing pages into the wrong vma.

By installing the page into a writable vma, it becomes possible to write
to your own binder pages, which are normally read-only. Although you're
not supposed to be able to write to those pages, the intent behind the
design of Rust Binder is that even if you get that ability, it should not
lead to anything bad. Unfortunately, due to another bug, that is not the
case.

To fix this, store a pointer in vm_private_data and check that the vma
returned by vma_lookup() has the right vm_ops and vm_private_data before
trying to use the vma. This should ensure that Rust Binder will refuse
to interact with any other VMA. The plan is to introduce more vma
abstractions to avoid this unsafe access to vm_ops and vm_private_data,
but for now let's start with the simplest possible fix.

C Binder performs the same check in a slightly different way: it
provides a vm_ops->close that sets a boolean to true, then checks that
boolean after calling vma_lookup(), but this is more fragile
than the solution in this patch. (We probably still want to do both, but
the vm_ops->close callback will be added later as part of the follow-up
vma API changes.)

It's still possible to remap the vma so that pages appear in the right
vma, but at the wrong offset, but this is a separate issue and will be
fixed when Rust Binder gets a vm_ops->close callback.

## References
- https://git.kernel.org/stable/c/20a01f20d1f4064d90a8627aa41b5987f0220bb9
- https://git.kernel.org/stable/c/5a472d04fb4b9115fb7d1535bd885cea450f14db
- https://git.kernel.org/stable/c/8ef2c15aeae07647f530d30f6daaf79eb801bcd1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43434.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
