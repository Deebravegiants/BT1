# [M] netfs, fscache: Prevent Oops in fscache_put_cache()

## Summary
Severity: Medium
Advisory: CVE-2024-26612
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-26612
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs, fscache: Prevent Oops in fscache_put_cache()

This function dereferences "cache" and then checks if it's
IS_ERR_OR_NULL().  Check first, then dereference.

## References
- https://git.kernel.org/stable/c/1c45256e599061021e2c848952e50f406457e448
- https://git.kernel.org/stable/c/3be0b3ed1d76c6703b9ee482b55f7e01c369cc68
- https://git.kernel.org/stable/c/4200ad3e46ce50f410fdda302745489441bc70f0
- https://git.kernel.org/stable/c/82a9bc343ba019665d3ddc1d9a180bf0e0390cf3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26612.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26612
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
