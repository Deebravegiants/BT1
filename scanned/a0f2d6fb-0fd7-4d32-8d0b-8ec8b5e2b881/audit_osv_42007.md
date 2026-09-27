# [H] crypto: pcrypt - restore callback for non-parallel fallback

## Summary
Severity: High
Advisory: CVE-2026-64312
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64312
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: pcrypt - restore callback for non-parallel fallback

pcrypt installs pcrypt_aead_done() on the child AEAD request before
trying to submit it through padata.  If padata_do_parallel() returns
-EBUSY, pcrypt falls back to calling the child AEAD directly.

That fallback must not keep the padata completion callback.  Otherwise
an asynchronous completion runs pcrypt_aead_done() even though the
request was never enrolled in padata.

Restore the original request callback and callback data before calling
the child AEAD directly.  This keeps the fallback path aligned with a
direct AEAD request while leaving the parallel path unchanged.

## References
- https://git.kernel.org/stable/c/3920c5f6edc341729d20d0507e466c6d3b11f372
- https://git.kernel.org/stable/c/4711ca06bd169a2cbc9cc59a6de2ed512c41a880
- https://git.kernel.org/stable/c/81ce16d938db9b88cdc231522c0358395ae8c6b5
- https://git.kernel.org/stable/c/82789a44415e3e31168229421b138278dfb16412
- https://git.kernel.org/stable/c/83fa1397d5853de1e27dd52ec44b068ff358ca18
- https://git.kernel.org/stable/c/ae93c5b3e2a2968b56d772ca1d06615927b7cc36
- https://git.kernel.org/stable/c/c4bd2f4c35b0e15b6040c2f7e7e7986780c066cf
- https://git.kernel.org/stable/c/ed459fe319376e876de433d12b6c6772e612ca36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64312.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64312
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
