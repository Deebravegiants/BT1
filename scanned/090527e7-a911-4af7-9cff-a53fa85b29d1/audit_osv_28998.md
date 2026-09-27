# [H] RDMA/hns: Modify the print level of CQE error

## Summary
Severity: High
Advisory: CVE-2024-38590
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38590
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Modify the print level of CQE error

Too much print may lead to a panic in kernel. Change ibdev_err() to
ibdev_err_ratelimited(), and change the printing level of cqe dump
to debug level.

## References
- https://git.kernel.org/stable/c/06cf121346bbd3d83a5eea05bb87666c6b279990
- https://git.kernel.org/stable/c/17f3741c65c4a042ae8ba094068b07a4b77e213c
- https://git.kernel.org/stable/c/349e859952285ab9689779fb46de163f13f18f43
- https://git.kernel.org/stable/c/45b31be4dd22827903df15c548b97b416790139b
- https://git.kernel.org/stable/c/6f541a89ced8305da459e3ab0006e7528cf7da7b
- https://git.kernel.org/stable/c/817a10a6df9354e67561922d2b7fce48dfbebc55
- https://git.kernel.org/stable/c/cc699b7eb2bc963c12ffcd37f80f45330d2924bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38590.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38590
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
