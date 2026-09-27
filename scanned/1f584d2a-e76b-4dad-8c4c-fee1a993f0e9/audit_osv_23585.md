# [H] btrfs: do not clean up repair bio if submit fails

## Summary
Severity: High
Advisory: CVE-2022-49168
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49168
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.248, >=5.11.0 <5.15.184, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: do not clean up repair bio if submit fails

The submit helper will always run bio_endio() on the bio if it fails to
submit, so cleaning up the bio just leads to a variety of use-after-free
and NULL pointer dereference bugs because we race with the endio
function that is cleaning up the bio.  Instead just return BLK_STS_OK as
the repair function has to continue to process the rest of the pages,
and the endio for the repair bio will do the appropriate cleanup for the
page that it was given.

## References
- https://git.kernel.org/stable/c/7170875083254b51fcc5d67f96640977083f481e
- https://git.kernel.org/stable/c/8cbc3001a3264d998d6b6db3e23f935c158abd4d
- https://git.kernel.org/stable/c/d1cb11fb45ebbb1e7dfe5e9038b32ea72c184b14
- https://git.kernel.org/stable/c/e76c78c48902dae6fa612749f59162bca0a79e0b
- https://git.kernel.org/stable/c/e7e1d15d2bd8c373cf621614ddd17971a2132713
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49168.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49168
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
