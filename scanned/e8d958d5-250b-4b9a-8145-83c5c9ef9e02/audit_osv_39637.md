# [H] ptrace: slightly saner 'get_dumpable()' logic

## Summary
Severity: High
Advisory: CVE-2026-46333
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-46333
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.256, >=5.11.0 <5.15.207, >=5.16.0 <6.1.173, >=6.2.0 <6.6.139, >=6.7.0 <6.12.89, >=6.13.0 <6.18.31, >=6.19.0 <7.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptrace: slightly saner 'get_dumpable()' logic

The 'dumpability' of a task is fundamentally about the memory image of
the task - the concept comes from whether it can core dump or not - and
makes no sense when you don't have an associated mm.

And almost all users do in fact use it only for the case where the task
has a mm pointer.

But we have one odd special case: ptrace_may_access() uses 'dumpable' to
check various other things entirely independently of the MM (typically
explicitly using flags like PTRACE_MODE_READ_FSCREDS).  Including for
threads that no longer have a VM (and maybe never did, like most kernel
threads).

It's not what this flag was designed for, but it is what it is.

The ptrace code does check that the uid/gid matches, so you do have to
be uid-0 to see kernel thread details, but this means that the
traditional "drop capabilities" model doesn't make any difference for
this all.

Make it all make a *bit* more sense by saying that if you don't have a
MM pointer, we'll use a cached "last dumpability" flag if the thread
ever had a MM (it will be zero for kernel threads since it is never
set), and require a proper CAP_SYS_PTRACE capability to override.

## References
- http://www.openwall.com/lists/oss-security/2026/05/15/9
- http://www.openwall.com/lists/oss-security/2026/05/20/14
- http://www.openwall.com/lists/oss-security/2026/05/20/16
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/01363cb3fbd0238ffdeb09f53e9039c9edf8a730
- https://git.kernel.org/stable/c/15b828a46f305ae9f05a7c16914b3ce273474205
- https://git.kernel.org/stable/c/2a93a4fac7b6051d3be7cd1b015fe7320cd0404d
- https://git.kernel.org/stable/c/31e62c2ebbfdc3fe3dbdf5e02c92a9dc67087a3a
- https://git.kernel.org/stable/c/4709234fd1b95136ceb789f639b1e7ea5de1b181
- https://git.kernel.org/stable/c/6e5b51e74a40d377bcd3081dd33fbaa0e1aa7e3d
- https://git.kernel.org/stable/c/8f907d345bae8f4b3f004c5abc56bf2dfb851ea7
- https://git.kernel.org/stable/c/93d4ba49d18e3d7fb41a9927c2d0cca5e9dfefd6
- https://lists.debian.org/debian-lts-announce/2026/05/msg00032.html
- https://lists.debian.org/debian-lts-announce/2026/05/msg00035.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46333.json
- https://access.redhat.com/errata/RHSA-2026:19521
- https://access.redhat.com/errata/RHSA-2026:19540
- https://access.redhat.com/errata/RHSA-2026:19568
- https://access.redhat.com/errata/RHSA-2026:19569
- https://access.redhat.com/errata/RHSA-2026:19664
