# [H] thunderbolt: Limit XDomain response copy to actual frame size

## Summary
Severity: High
Advisory: CVE-2026-53146
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53146
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: Limit XDomain response copy to actual frame size

tb_xdomain_copy() copies req->response_size bytes from the received
packet buffer regardless of the actual frame size.  When a short
response arrives, this reads past the valid frame data in the DMA
pool buffer into stale contents from previous transactions.

Use the minimum of frame size and expected response size for the
copy length.

## References
- https://git.kernel.org/stable/c/033dfa63bf6be2653441a1dccae4a8313a91bb9d
- https://git.kernel.org/stable/c/4db2bd2ed4785dbadaeeab9f4e346b21ac5fb8eb
- https://git.kernel.org/stable/c/7720654b4842bcdfeb64bc002f6186041849e1e7
- https://git.kernel.org/stable/c/a15b6d3136accb2bf84b04d9a3ddd991f7fbf1cb
- https://git.kernel.org/stable/c/b2c1e5d9f1598cc1a4736d5c6bd1218f90805ee4
- https://git.kernel.org/stable/c/b5daa920f44cb582272fc9bfaeb67408776cbaef
- https://git.kernel.org/stable/c/c55da494dfb445fb28df3a9d293c2be6a299cd01
- https://git.kernel.org/stable/c/fc261397295b8ad0654cec747b0ec25ea0011995
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53146.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53146
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
