# [H] zram: fix use-after-free in zram_bvec_write_partial()

## Summary
Severity: High
Advisory: CVE-2026-53185
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53185
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

zram: fix use-after-free in zram_bvec_write_partial()

zram_read_page() picks the sync or async backing device read path based on
whether the parent bio is NULL.  zram_bvec_write_partial() passes its
parent bio down, so for ZRAM_WB slots the read is dispatched
asynchronously and zram_read_page() returns 0 while the bio is still in
flight.  The caller then runs memcpy_from_bvec(), zram_write_page() and
__free_page() on the buffer, leaving the async read to write into a freed
page.

zram_bvec_read_partial() was switched to NULL in commit 4e3c87b9421d
("zram: fix synchronous reads") for the same reason; the write_partial
counterpart was missed.

## References
- https://git.kernel.org/stable/c/0c2821665ff71be3f4b07ecece384669f2877f6a
- https://git.kernel.org/stable/c/198b5a14cca27263b9c14b20114c8092de15dfcb
- https://git.kernel.org/stable/c/732fd9f0b9c1cdc6dfd77162ded60df005182cc0
- https://git.kernel.org/stable/c/77a602b505ce4802915853cfc435a4722fab3e64
- https://git.kernel.org/stable/c/c96786d6ff1acc1d54d9241e97767554c1dfdd5b
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53185.json
- https://access.redhat.com/errata/RHSA-2026:59723
- https://access.redhat.com/errata/RHSA-2026:61887
- https://access.redhat.com/errata/RHSA-2026:63013
- https://access.redhat.com/errata/RHSA-2026:63014
- https://access.redhat.com/errata/RHSA-2026:65708
- https://access.redhat.com/security/cve/CVE-2026-53185
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53185.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53185
- https://bugzilla.redhat.com/show_bug.cgi?id=2492735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
