# [C] s390/vfio_ccw: Ensure first IDAW remains constant

## Summary
Severity: Critical
Advisory: CVE-2026-80551
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80551
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.6.154, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Ensure first IDAW remains constant

The first IDAW in a list does not need to be on a 2K/4K boundary
like all others, and so is read separately to accurately calculate
the size of the buffer needed to read the full IDAL.

Verify that the address found in the first IDAW is unchanged between
reads, to ensure a consistent set of IDAWs being worked with.

## References
- https://git.kernel.org/stable/c/08ef2a82115690d6e229615872ac1731af732497
- https://git.kernel.org/stable/c/0d46c2565f173bcddcdcaf44a4f69789a20535e2
- https://git.kernel.org/stable/c/460b977a4e71cc319fdadf91c193ec3beaa57263
- https://git.kernel.org/stable/c/565bef268d75bf7df665bce6923a88cd0eb74592
- https://git.kernel.org/stable/c/fc59e9482117ebdccd6dc7fa8082f8b980fd021e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80551.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80551
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
