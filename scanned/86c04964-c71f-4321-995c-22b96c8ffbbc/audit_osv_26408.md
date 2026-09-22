# [H] xsk: Add missing overflow check in xdp_umem_reg

## Summary
Severity: High
Advisory: CVE-2023-53080
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53080
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.177, >=5.11.0 <5.15.105, >=5.16.0 <6.1.22, >=6.2.0 <6.2.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: Add missing overflow check in xdp_umem_reg

The number of chunks can overflow u32. Make sure to return -EINVAL on
overflow. Also remove a redundant u32 cast assigning umem->npgs.

## References
- https://git.kernel.org/stable/c/3cfc3564411acf96bf2fb791f706a1aa4f872c1d
- https://git.kernel.org/stable/c/580634b03a55f04a3c1968bcbd97736c079c6601
- https://git.kernel.org/stable/c/a069909acc4435eeb41d05ccc03baa447cc01b7e
- https://git.kernel.org/stable/c/bb2e3bfb2a79db0c2057c6f701b782954394c67f
- https://git.kernel.org/stable/c/c7df4813b149362248d6ef7be41a311e27bf75fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53080.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53080
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
