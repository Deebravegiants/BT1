# [H] cachefiles: add consistency check for copen/cread

## Summary
Severity: High
Advisory: CVE-2024-41075
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41075
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

cachefiles: add consistency check for copen/cread

This prevents malicious processes from completing random copen/cread
requests and crashing the system. Added checks are listed below:

  * Generic, copen can only complete open requests, and cread can only
    complete read requests.
  * For copen, ondemand_id must not be 0, because this indicates that the
    request has not been read by the daemon.
  * For cread, the object corresponding to fd and req should be the same.

## References
- https://git.kernel.org/stable/c/36d845ccd7bf527110a65fe953886a176c209539
- https://git.kernel.org/stable/c/3b744884c0431b5a62c92900e64bfd0ed61e8e2a
- https://git.kernel.org/stable/c/8aaa6c5dd2940ab934d6cd296175f43dbb32b34a
- https://git.kernel.org/stable/c/a26dc49df37e996876f50a0210039b2d211fdd6f
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41075.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
