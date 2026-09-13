# [M] net/mlx5: DR, prevent potential error pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2024-56660
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56660
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: DR, prevent potential error pointer dereference

The dr_domain_add_vport_cap() function generally returns NULL on error
but sometimes we want it to return ERR_PTR(-EBUSY) so the caller can
retry.  The problem here is that "ret" can be either -EBUSY or -ENOMEM
and if it's and -ENOMEM then the error pointer is propogated back and
eventually dereferenced in dr_ste_v0_build_src_gvmi_qpn_tag().

## References
- https://git.kernel.org/stable/c/11776cff0b563c8b8a4fa76cab620bfb633a8cb8
- https://git.kernel.org/stable/c/325cf73a1b449fea3158ab99d03a7a717aad1618
- https://git.kernel.org/stable/c/61f720e801443d4e2a3c0261eda4ad8431458dca
- https://git.kernel.org/stable/c/a59c61a1869ceefc65ef02886f91e8cd0062211f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56660.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56660
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
