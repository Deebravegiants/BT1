# [H] RDMA/siw: Fix potential NULL pointer dereference in header processing

## Summary
Severity: High
Advisory: CVE-2026-23242
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23242
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Fix potential NULL pointer dereference in header processing

If siw_get_hdr() returns -EINVAL before set_rx_fpdu_context(),
qp->rx_fpdu can be NULL. The error path in siw_tcp_rx_data()
dereferences qp->rx_fpdu->more_ddp_segs without checking, which
may lead to a NULL pointer deref. Only check more_ddp_segs when
rx_fpdu is present.

KASAN splat:
[  101.384271] KASAN: null-ptr-deref in range [0x00000000000000c0-0x00000000000000c7]
[  101.385869] RIP: 0010:siw_tcp_rx_data+0x13ad/0x1e50

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/14ab3da122bd18920ad57428f6cf4fade8385142
- https://git.kernel.org/stable/c/714c99e1dc8f85f446e05be02ba83972e981a817
- https://git.kernel.org/stable/c/8564dcc12fbb372d984ab45768cae9335777b274
- https://git.kernel.org/stable/c/87b7a036d2c73d5bb3ae2d47dee23de465db3355
- https://git.kernel.org/stable/c/ab61841633d10e56a58c1493a262f0d02dba2f5e
- https://git.kernel.org/stable/c/ab957056192d6bd068b3759cb2077d859cca01f0
- https://git.kernel.org/stable/c/ce025f7f5d070596194315eb2e4e89d568b8a755
- https://git.kernel.org/stable/c/ffba40b67663567481fa8a1ed5d2da36897c175d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23242.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
