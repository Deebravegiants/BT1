# [M] xfrm: validate new SA's prefixlen using SA family when sel.family is unset

## Summary
Severity: Medium
Advisory: CVE-2024-50142
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50142
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: validate new SA's prefixlen using SA family when sel.family is unset

This expands the validation introduced in commit 07bf7908950a ("xfrm:
Validate address prefix lengths in the xfrm selector.")

syzbot created an SA with
    usersa.sel.family = AF_UNSPEC
    usersa.sel.prefixlen_s = 128
    usersa.family = AF_INET

Because of the AF_UNSPEC selector, verify_newsa_info doesn't put
limits on prefixlen_{s,d}. But then copy_from_user_state sets
x->sel.family to usersa.family (AF_INET). Do the same conversion in
verify_newsa_info before validating prefixlen_{s,d}, since that's how
prefixlen is going to be used later on.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2d08a6c31c65f23db71a5385ee9cf9d8f9a67a71
- https://git.kernel.org/stable/c/3f0ab59e6537c6a8f9e1b355b48f9c05a76e8563
- https://git.kernel.org/stable/c/401ad99a5ae7180dd9449eac104cb755f442e7f3
- https://git.kernel.org/stable/c/7d9868180bd1e4cf37e7c5067362658971162366
- https://git.kernel.org/stable/c/8df5cd51fd70c33aa1776e5cbcd82b0a86649d73
- https://git.kernel.org/stable/c/bce1afaa212ec380bf971614f70909a27882b862
- https://git.kernel.org/stable/c/e68dd80ba498265d2266b12dc3459164f4ff0c4a
- https://git.kernel.org/stable/c/f31398570acf0f0804c644006f7bfa9067106b0a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50142.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50142
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
