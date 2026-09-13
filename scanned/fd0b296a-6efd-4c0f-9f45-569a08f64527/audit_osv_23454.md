# [C] NFSD: Fix NFSv3 SETATTR/CREATE's handling of large file sizes

## Summary
Severity: Critical
Advisory: CVE-2022-48829
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48829
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.295, >=5.5.0 <5.10.220, >=5.11.0 <5.15.24, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix NFSv3 SETATTR/CREATE's handling of large file sizes

iattr::ia_size is a loff_t, so these NFSv3 procedures must be
careful to deal with incoming client size values that are larger
than s64_max without corrupting the value.

Silently capping the value results in storing a different value
than the client passed in which is unexpected behavior, so remove
the min_t() check in decode_sattr3().

Note that RFC 1813 permits only the WRITE procedure to return
NFS3ERR_FBIG. We believe that NFSv3 reference implementations
also return NFS3ERR_FBIG when ia_size is too large.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/37f2d2cd8eadddbbd9c7bda327a9393399b2f89b
- https://git.kernel.org/stable/c/72c14aed6838b5d90b4dd926b6a339b34bb02e08
- https://git.kernel.org/stable/c/a231ae6bb50e7c0a9e9efd7b0d10687f1d71b3a3
- https://git.kernel.org/stable/c/a648fdeb7c0e17177a2280344d015dba3fbe3314
- https://git.kernel.org/stable/c/aa9051ddb4b378bd22e72a67bc77b9fc1482c5f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48829.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48829
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
