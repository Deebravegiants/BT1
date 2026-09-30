# [C] NFSD: Fix SECINFO_NO_NAME decode error cleanup

## Summary
Severity: Critical
Advisory: CVE-2026-53398
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53398
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.1.0 <6.6.144, >=6.2.0 <6.12.95, >=6.7.0 <6.18.38, >=6.13.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix SECINFO_NO_NAME decode error cleanup

nfsd4_decode_secinfo_no_name() currently initializes sin_exp after
decoding sin_style. If the XDR stream is truncated, the decoder returns
nfserr_bad_xdr before sin_exp is initialized.

Since commit 3fdc54646234 ("NFSD: Reduce amount of struct
nfsd4_compoundargs that needs clearing"), the inline iops array is not
cleared between RPC calls. A failed SECINFO_NO_NAME decode can therefore
leave sin_exp holding stale union contents from a previous operation.

The error response path still invokes nfsd4_secinfo_no_name_release(),
which calls exp_put() on a non-NULL sin_exp.

Initialize sin_exp before the first failable decode step, matching
nfsd4_decode_secinfo().

## References
- https://git.kernel.org/stable/c/161d1aaeb04d620d3692639700512bb5038c1e10
- https://git.kernel.org/stable/c/1e04be34cafae119e82bcaccd6d28a20f72a3647
- https://git.kernel.org/stable/c/46eb17d45be69d28c7a23ea03283b207426a8232
- https://git.kernel.org/stable/c/49de5d31dd8fdebf78bdeaf196b0ca5cd5c75439
- https://git.kernel.org/stable/c/5ec37edcb534f3fc92304be236d37f08e6545585
- https://git.kernel.org/stable/c/8836405abdc53ca3dd5fc68b2cf6f8f012fad011
- https://git.kernel.org/stable/c/9e18e83b8846a5c3fe13fc8a464b4865d33996c6
- https://git.kernel.org/stable/c/c8a24effd96d4779e2ad779654682304491c55a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53398.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53398
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
