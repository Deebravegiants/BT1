# [H] ublk: detach gendisk from ublk device if add_disk() fails

## Summary
Severity: High
Advisory: CVE-2024-56764
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-56764
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ublk: detach gendisk from ublk device if add_disk() fails

Inside ublk_abort_requests(), gendisk is grabbed for aborting all
inflight requests. And ublk_abort_requests() is called when exiting
the uring context or handling timeout.

If add_disk() fails, the gendisk may have been freed when calling
ublk_abort_requests(), so use-after-free can be caused when getting
disk's reference in ublk_abort_requests().

Fixes the bug by detaching gendisk from ublk device if add_disk() fails.

## References
- https://git.kernel.org/stable/c/75cd4005da5492129917a4a4ee45e81660556104
- https://git.kernel.org/stable/c/7d680f2f76a3417fdfc3946da7471e81464f7b41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56764.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56764
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
