# [H] crypto: af_alg - Set merge to zero early in af_alg_sendmsg

## Summary
Severity: High
Advisory: CVE-2025-39931
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39931
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: af_alg - Set merge to zero early in af_alg_sendmsg

If an error causes af_alg_sendmsg to abort, ctx->merge may contain
a garbage value from the previous loop.  This may then trigger a
crash on the next entry into af_alg_sendmsg when it attempts to do
a merge that can't be done.

Fix this by setting ctx->merge to zero near the start of the loop.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/045ee26aa3920a47ec46d7fcb302420bf01fd753
- https://git.kernel.org/stable/c/2374c11189ef704a3e4863646369f1b8e6a27d71
- https://git.kernel.org/stable/c/24c1106504c625fabd3b7229611af617b4c27ac7
- https://git.kernel.org/stable/c/28f6f37abca7c5c9eb3959c66310f1d4d98b8aaf
- https://git.kernel.org/stable/c/6241b9e2809b12da9130894cf5beddf088dc1b8a
- https://git.kernel.org/stable/c/9574b2330dbd2b5459b74d3b5e9619d39299fc6f
- https://git.kernel.org/stable/c/db2b42425dfbde4983b0c20fb7cfa05f70e6a745
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39931.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39931
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
