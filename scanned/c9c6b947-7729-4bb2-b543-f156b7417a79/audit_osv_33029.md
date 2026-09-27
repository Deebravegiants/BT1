# [H] padata: Fix pd UAF once and for all

## Summary
Severity: High
Advisory: CVE-2025-38584
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38584
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

padata: Fix pd UAF once and for all

There is a race condition/UAF in padata_reorder that goes back
to the initial commit.  A reference count is taken at the start
of the process in padata_do_parallel, and released at the end in
padata_serial_worker.

This reference count is (and only is) required for padata_replace
to function correctly.  If padata_replace is never called then
there is no issue.

In the function padata_reorder which serves as the core of padata,
as soon as padata is added to queue->serial.list, and the associated
spin lock released, that padata may be processed and the reference
count on pd would go away.

Fix this by getting the next padata before the squeue->serial lock
is released.

In order to make this possible, simplify padata_reorder by only
calling it once the next padata arrives.

## References
- https://git.kernel.org/stable/c/609e59193fc6d9dd323f1c6ae1fdd721f1c79680
- https://git.kernel.org/stable/c/71203f68c7749609d7fc8ae6ad054bdedeb24f91
- https://git.kernel.org/stable/c/73f132e60857038416540c3599b1de6033d7575a
- https://git.kernel.org/stable/c/a11a12a9880ab37342b73c93cfe1a3ada02ff0db
- https://git.kernel.org/stable/c/a2048e475e22b13dc3e53d485b7e6e11464ed9a6
- https://git.kernel.org/stable/c/cdf79bd2e1ecb3cc75631c73d8f4149be6019a52
- https://git.kernel.org/stable/c/dbe3e911a59bda6de96e7cae387ff882c2c177fa
- https://git.kernel.org/stable/c/f231d5d001ec75f5886c02d496a4c79edc383d45
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38584.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38584
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
