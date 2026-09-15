# [H] s390/vfio_ccw: Selectively expand io_mutex

## Summary
Severity: High
Advisory: CVE-2026-80548
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80548
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Selectively expand io_mutex

The io_mutex was defined to serialize the io_regions, but then has
also sort of been associated with the I/O themselves because of
the close relationship they share.

With the handful of races that are possible, the choices are either to:
 A) expand the scope of io_mutex to close these remaining windows, or
 B) reduce the scope of io_mutex to just io_region, and introduce a new
    lock mechanism for the remaining I/O resources

This patch implements A, since B brings with it a lot more interactions
that would need to be tracked and kept in a correct hierarchy. It also
takes advantage of the workqueue element for cp_free() that now gets
called out of fsm_notoper(), which could be invoked out of an interrupt
context and thus cannot acquire a mutex itself.

## References
- https://git.kernel.org/stable/c/2a5ac0c0f1f7da33929211a2e41911bf72ee35d8
- https://git.kernel.org/stable/c/2ba9efdf9ebedc4e54df4b56aa3b43a65f7967cd
- https://git.kernel.org/stable/c/34f4feff3e90bd09308fad0974e97113b23b812a
- https://git.kernel.org/stable/c/56d7488533ceac4e986e96e15c9e487a2245bc01
- https://git.kernel.org/stable/c/b6aecea4b2b246f9fbd98a5712daa1193a60818e
- https://git.kernel.org/stable/c/dab6a6627b0b0cce23653e99c7b0bf8c6cfd82e0
- https://git.kernel.org/stable/c/f72a51810d49411bd8cad0c2df8592320a2fe5cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80548.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80548
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
