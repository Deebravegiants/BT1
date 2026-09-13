# [C] scsi: lpfc: Fix buffer free/clear order in deferred receive path

## Summary
Severity: Critical
Advisory: CVE-2025-39841
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39841
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.299, >=5.5.0 <5.10.243, >=5.11.0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Fix buffer free/clear order in deferred receive path

Fix a use-after-free window by correcting the buffer release sequence in
the deferred receive path. The code freed the RQ buffer first and only
then cleared the context pointer under the lock. Concurrent paths (e.g.,
ABTS and the repost path) also inspect and release the same pointer under
the lock, so the old order could lead to double-free/UAF.

Note that the repost path already uses the correct pattern: detach the
pointer under the lock, then free it after dropping the lock. The
deferred path should do the same.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://git.kernel.org/stable/c/367cb5ffd8a8a4c85dc89f55e7fa7cc191425b11
- https://git.kernel.org/stable/c/55658c7501467ca9ef3bd4453dd920010db8bc13
- https://git.kernel.org/stable/c/897f64b01c1249ac730329b83f4f40bab71e86c7
- https://git.kernel.org/stable/c/95b63d15fce5c54a73bbf195e1aacb5a75b128e2
- https://git.kernel.org/stable/c/9dba9a45c348e8460da97c450cddf70b2056deb3
- https://git.kernel.org/stable/c/ab34084f42ee06a9028d67c78feafb911d33d111
- https://git.kernel.org/stable/c/baa39f6ad79d372a6ce0aa639fbb2f1578479f57
- https://git.kernel.org/stable/c/d96cc9a1b57725930c60b607423759d563b4d900
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39841.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39841
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
