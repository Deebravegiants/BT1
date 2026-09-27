# [M] SUNRPC: fix a memleak in gss_import_v2_context

## Summary
Severity: Medium
Advisory: CVE-2023-52653
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2023-52653
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: fix a memleak in gss_import_v2_context

The ctx->mech_used.data allocated by kmemdup is not freed in neither
gss_import_v2_context nor it only caller gss_krb5_import_sec_context,
which frees ctx on error.

Thus, this patch reform the last call of gss_import_v2_context to the
gss_krb5_import_ctx_v2, preventing the memleak while keepping the return
formation.

## References
- https://git.kernel.org/stable/c/47ac11db93e74ac49cd6c3fc69bcbc5964c4a8b4
- https://git.kernel.org/stable/c/99044c01ed5329e73651c054d8a4baacdbb1a27c
- https://git.kernel.org/stable/c/d111e30d9cd846bb368faf3637dc0f71fcbcf822
- https://git.kernel.org/stable/c/e67b652d8e8591d3b1e569dbcdfcee15993e91fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52653.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52653
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
