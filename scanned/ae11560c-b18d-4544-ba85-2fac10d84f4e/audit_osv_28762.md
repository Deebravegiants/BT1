# [C] SUNRPC: Fix loop termination condition in gss_free_in_token_pages()

## Summary
Severity: Critical
Advisory: CVE-2024-36288
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-36288
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.3 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: Fix loop termination condition in gss_free_in_token_pages()

The in_token->pages[] array is not NULL terminated. This results in
the following KASAN splat:

  KASAN: maybe wild-memory-access in range [0x04a2013400000008-0x04a201340000000f]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/0a1cb0c6102bb4fd310243588d39461da49497ad
- https://git.kernel.org/stable/c/4a77c3dead97339478c7422eb07bf4bf63577008
- https://git.kernel.org/stable/c/4cefcd0af7458bdeff56a9d8dfc6868ce23d128a
- https://git.kernel.org/stable/c/57ff6c0a175930856213b2aa39f8c845a53e5b1c
- https://git.kernel.org/stable/c/6ed45d20d30005bed94c8c527ce51d5ad8121018
- https://git.kernel.org/stable/c/af628d43a822b78ad8d4a58d8259f8bf8bc71115
- https://git.kernel.org/stable/c/b4878ea99f2b40ef1925720b1b4ca7f4af1ba785
- https://git.kernel.org/stable/c/f9977e4e0cd98a5f06f2492b4f3547db58deabf5
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36288.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
