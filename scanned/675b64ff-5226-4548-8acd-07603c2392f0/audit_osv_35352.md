# [H] crypto: seqiv - Do not use req->iv after crypto_aead_encrypt

## Summary
Severity: High
Advisory: CVE-2025-71131
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71131
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: seqiv - Do not use req->iv after crypto_aead_encrypt

As soon as crypto_aead_encrypt is called, the underlying request
may be freed by an asynchronous completion.  Thus dereferencing
req->iv after it returns is invalid.

Instead of checking req->iv against info, create a new variable
unaligned_info and use it for that purpose instead.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0279978adec6f1296af66b642cce641c6580be46
- https://git.kernel.org/stable/c/18202537856e0fae079fed2c9308780bcff2bb9d
- https://git.kernel.org/stable/c/50f196d2bbaee4ab2494bb1b0d294deba292951a
- https://git.kernel.org/stable/c/50fdb78b7c0bcc550910ef69c0984e751cac72fa
- https://git.kernel.org/stable/c/5476f7f8a311236604b78fcc5b2a63b3a61b0169
- https://git.kernel.org/stable/c/baf0e2d1e03ddb04781dfe7f22a654d3611f69b2
- https://git.kernel.org/stable/c/ccbb96434d88e32358894c879457b33f7508e798
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71131.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71131
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
