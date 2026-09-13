# [H] KVM: x86: Mark target gfn of emulated atomic instruction as dirty

## Summary
Severity: High
Advisory: CVE-2024-35804
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35804
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.154, >=5.16.0 <6.1.84, >=5.19.0 <6.6.24, >=6.2.0 <6.7.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Mark target gfn of emulated atomic instruction as dirty

When emulating an atomic access on behalf of the guest, mark the target
gfn dirty if the CMPXCHG by KVM is attempted and doesn't fault.  This
fixes a bug where KVM effectively corrupts guest memory during live
migration by writing to guest memory without informing userspace that the
page is dirty.

Marking the page dirty got unintentionally dropped when KVM's emulated
CMPXCHG was converted to do a user access.  Before that, KVM explicitly
mapped the guest page into kernel memory, and marked the page dirty during
the unmap phase.

Mark the page dirty even if the CMPXCHG fails, as the old data is written
back on failure, i.e. the page is still written.  The value written is
guaranteed to be the same because the operation is atomic, but KVM's ABI
is that all writes are dirty logged regardless of the value written.  And
more importantly, that's what KVM did before the buggy commit.

Huge kudos to the folks on the Cc list (and many others), who did all the
actual work of triaging and debugging.

base-commit: 6769ea8da8a93ed4630f1ce64df6aafcaabfce64

## References
- https://git.kernel.org/stable/c/225d587a073584946c05c9b7651d637bd45c0c71
- https://git.kernel.org/stable/c/726374dde5d608b15b9756bd52b6fc283fda7a06
- https://git.kernel.org/stable/c/910c57dfa4d113aae6571c2a8b9ae8c430975902
- https://git.kernel.org/stable/c/9d1b22e573a3789ed1f32033ee709106993ba551
- https://git.kernel.org/stable/c/a9bd6bb6f02bf7132c1ab192ba62bbfa52df7d66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35804.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35804
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
