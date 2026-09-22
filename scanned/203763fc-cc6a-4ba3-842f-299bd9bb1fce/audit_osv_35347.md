# [H] SUNRPC: svcauth_gss: avoid NULL deref on zero length gss_token in gss_read_proxy_verf

## Summary
Severity: High
Advisory: CVE-2025-71120
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71120
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: svcauth_gss: avoid NULL deref on zero length gss_token in gss_read_proxy_verf

A zero length gss_token results in pages == 0 and in_token->pages[0]
is NULL. The code unconditionally evaluates
page_address(in_token->pages[0]) for the initial memcpy, which can
dereference NULL even when the copy length is 0. Guard the first
memcpy so it only runs when length > 0.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1c8bb965e9b0559ff0f5690615a527c30f651dd8
- https://git.kernel.org/stable/c/4dedb6a11243a5c9eb9dbb97bca3c98bd725e83d
- https://git.kernel.org/stable/c/7452d53f293379e2c38cfa8ad0694aa46fc4788b
- https://git.kernel.org/stable/c/a2c6f25ab98b423f99ccd94874d655b8bcb01a19
- https://git.kernel.org/stable/c/a8f1e445ce3545c90d69c9e8ff8f7821825fe810
- https://git.kernel.org/stable/c/d4b69a6186b215d2dc1ebcab965ed88e8d41768d
- https://git.kernel.org/stable/c/f9e53f69ac3bc4ef568b08d3542edac02e83fefd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71120.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
