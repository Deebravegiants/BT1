# [C] nfsd: handle get_client_locked() failure in nfsd4_setclientid_confirm()

## Summary
Severity: Critical
Advisory: CVE-2025-38724
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38724
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: handle get_client_locked() failure in nfsd4_setclientid_confirm()

Lei Lu recently reported that nfsd4_setclientid_confirm() did not check
the return value from get_client_locked(). a SETCLIENTID_CONFIRM could
race with a confirmed client expiring and fail to get a reference. That
could later lead to a UAF.

Fix this by getting a reference early in the case where there is an
extant confirmed client. If that fails then treat it as if there were no
confirmed client found at all.

In the case where the unconfirmed client is expiring, just fail and
return the result from get_client_locked().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/22f45cedf281e6171817c8a3432c44d788c550e1
- https://git.kernel.org/stable/c/36e83eda90e0e4ac52f259f775b40b2841f8a0a3
- https://git.kernel.org/stable/c/3f252a73e81aa01660cb426735eab932e6182e8d
- https://git.kernel.org/stable/c/571a5e46c71490285d2d8c06f6b5a7cbf6c7edd1
- https://git.kernel.org/stable/c/74ad36ed60df561a303a19ecef400c7096b20306
- https://git.kernel.org/stable/c/908e4ead7f757504d8b345452730636e298cbf68
- https://git.kernel.org/stable/c/d35ac850410966010e92f401f4e21868a9ea4d8b
- https://git.kernel.org/stable/c/d71abd1ae4e0413707cd42b10c24a11d1aa71772
- https://git.kernel.org/stable/c/f3aac6cf390d8b80e1d82975faf4ac61175519c0
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38724.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38724
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
