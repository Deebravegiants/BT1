# [H] RDMA/mlx4: Prevent shift wrapping in set_user_sq_size()

## Summary
Severity: High
Advisory: CVE-2023-54168
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54168
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx4: Prevent shift wrapping in set_user_sq_size()

The ucmd->log_sq_bb_count variable is controlled by the user so this
shift can wrap.  Fix it by using check_shl_overflow() in the same way
that it was done in commit 515f60004ed9 ("RDMA/hns: Prevent undefined
behavior in hns_roce_set_user_sq_size()").

## References
- https://git.kernel.org/stable/c/196a6df08b08699ace4ce70e1efcdd9081b6565f
- https://git.kernel.org/stable/c/3ce0df3493277b9df275cb8455d9c677ae701230
- https://git.kernel.org/stable/c/3d5ae269c4bd392ec1edbfb3bd031b8f42d7feff
- https://git.kernel.org/stable/c/8feca625900777e02a449e53fe4121339934c38a
- https://git.kernel.org/stable/c/9911be2155720221a4f1f722b22bd0e2388d8bcf
- https://git.kernel.org/stable/c/9ad3221c86cc9c6305594b742d4a72dfbd4ea579
- https://git.kernel.org/stable/c/a183905869e692b6b7805b7472235585eff8e429
- https://git.kernel.org/stable/c/d50b3c73f1ac20dabc53dc6e9d64ce9c79a331eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54168.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54168
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
