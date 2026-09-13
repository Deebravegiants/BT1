# [C] NFSD: Fix nfsd4_encode_fattr4() crasher

## Summary
Severity: Critical
Advisory: CVE-2024-36958
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36958
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix nfsd4_encode_fattr4() crasher

Ensure that args.acl is initialized early. It is used in an
unconditional call to kfree() on the way out of
nfsd4_encode_fattr4().

## References
- https://git.kernel.org/stable/c/18180a4550d08be4eb0387fe83f02f703f92d4e7
- https://git.kernel.org/stable/c/6a7b07689af6e4e023404bf69b1230f43b2a15bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36958.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36958
- https://security.netapp.com/advisory/ntap-20250404-0007/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
