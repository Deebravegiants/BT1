# [H] net: nfc: fix races in nfc_llcp_sock_get() and nfc_llcp_sock_get_sn()

## Summary
Severity: High
Advisory: CVE-2023-52502
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52502
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <4.19.297, >=4.20.0 <5.4.259, >=5.5.0 <5.10.199, >=5.11.0 <5.15.136, >=5.16.0 <6.1.59, >=6.2.0 <6.5.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: nfc: fix races in nfc_llcp_sock_get() and nfc_llcp_sock_get_sn()

Sili Luo reported a race in nfc_llcp_sock_get(), leading to UAF.

Getting a reference on the socket found in a lookup while
holding a lock should happen before releasing the lock.

nfc_llcp_sock_get_sn() has a similar problem.

Finally nfc_llcp_recv_snl() needs to make sure the socket
found by nfc_llcp_sock_from_sn() does not disappear.

## References
- https://git.kernel.org/stable/c/31c07dffafce914c1d1543c135382a11ff058d93
- https://git.kernel.org/stable/c/6ac22ecdaad2ecc662048f8c6b0ceb1ca0699ef9
- https://git.kernel.org/stable/c/7adcf014bda16cdbf804af5c164d94d5d025db2d
- https://git.kernel.org/stable/c/d1af8a39cf839d93c8967fdd858f6bbdc3e4a15c
- https://git.kernel.org/stable/c/d888d3f70b0de32b4f51534175f039ddab15eef8
- https://git.kernel.org/stable/c/e4f2611f07c87b3ddb57c4b9e8efcd1e330fc3dc
- https://git.kernel.org/stable/c/e863f5720a5680e50c4cecf12424d7cc31b3eb0a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52502.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52502
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
