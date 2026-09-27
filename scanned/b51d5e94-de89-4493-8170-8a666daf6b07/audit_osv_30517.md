# [M] fs: Fix uninitialized value issue in from_kuid and from_kgid

## Summary
Severity: Medium
Advisory: CVE-2024-53101
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-53101
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.173, >=5.16.0 <6.1.118, >=6.2.0 <6.6.62, >=6.7.0 <6.11.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: Fix uninitialized value issue in from_kuid and from_kgid

ocfs2_setattr() uses attr->ia_mode, attr->ia_uid and attr->ia_gid in
a trace point even though ATTR_MODE, ATTR_UID and ATTR_GID aren't set.

Initialize all fields of newattrs to avoid uninitialized variables, by
checking if ATTR_MODE, ATTR_UID, ATTR_GID are initialized, otherwise 0.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/15f34347481648a567db67fb473c23befb796af5
- https://git.kernel.org/stable/c/17ecb40c5cc7755a321fb6148cba5797431ee5b8
- https://git.kernel.org/stable/c/1c28bca1256aecece6e94b26b85cd07e08b0dc90
- https://git.kernel.org/stable/c/1cb5bfc5bfc651982b6203c224d49b7ddacf28bc
- https://git.kernel.org/stable/c/5a72b0d3497b818d8f000c347a7c11801eb27bfc
- https://git.kernel.org/stable/c/9db25c2b41c34963c3ccf473b08171f87670652e
- https://git.kernel.org/stable/c/a0c77e5e3dcbffc7c6080ccc89c037f0c86496cf
- https://git.kernel.org/stable/c/b3e612bd8f64ce62e731e95f635e06a2efe3c80c
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53101.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53101
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
