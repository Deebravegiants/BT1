# [H] netfilter: nfnetlink: Initialise extack before use in ACKs

## Summary
Severity: High
Advisory: CVE-2024-44945
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-08-31
Source: https://osv.dev/vulnerability/CVE-2024-44945
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink: Initialise extack before use in ACKs

Add missing extack initialisation when ACKing BATCH_BEGIN and BATCH_END.

## References
- https://git.kernel.org/stable/c/3e03b536d9454c5802168b9e85248d456d3ff6a3
- https://git.kernel.org/stable/c/d1a7b382a9d3f0f3e5a80e0be2991c075fa4f618
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44945.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
