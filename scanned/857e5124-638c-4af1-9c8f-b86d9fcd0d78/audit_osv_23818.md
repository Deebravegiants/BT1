# [H] loop: implement ->free_disk

## Summary
Severity: High
Advisory: CVE-2022-49531
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49531
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

loop: implement ->free_disk

Ensure that the lo_device which is stored in the gendisk private
data is valid until the gendisk is freed.  Currently the loop driver
uses a lot of effort to make sure a device is not freed when it is
still in use, but to to fix a potential deadlock this will be relaxed
a bit soon.

## References
- https://git.kernel.org/stable/c/aadd1443aae7fe8956e3b11157827067f034406a
- https://git.kernel.org/stable/c/d2c7f56f8b5256d57f9e3fc7794c31361d43bdd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49531.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49531
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
