# [H] RDMA/mana_ib: boundary check before installing cq callbacks

## Summary
Severity: High
Advisory: CVE-2024-38542
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38542
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mana_ib: boundary check before installing cq callbacks

Add a boundary check inside mana_ib_install_cq_cb to prevent index overflow.

## References
- https://git.kernel.org/stable/c/168f6fbde0eabd71d1f4133df7d001a950b96977
- https://git.kernel.org/stable/c/f12afddfb142587d786df9e3cc4862190d3e2ec8
- https://git.kernel.org/stable/c/f79edef79b6a2161f4124112f9b0c46891bb0b74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38542.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38542
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
