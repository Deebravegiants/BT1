# [M] octeontx2-pf: handle otx2_mbox_get_rsp errors in otx2_flows.c

## Summary
Severity: Medium
Advisory: CVE-2024-56727
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56727
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.209, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: handle otx2_mbox_get_rsp errors in otx2_flows.c

Adding error pointer check after calling otx2_mbox_get_rsp().

## References
- https://git.kernel.org/stable/c/8c9f8b35dc3d4ad8053a72bc0c5a7843591f6b75
- https://git.kernel.org/stable/c/a479b3d7586e6f77f8337bbcac980eaf2d0a4029
- https://git.kernel.org/stable/c/bd3110bc102ab6292656b8118be819faa0de8dd0
- https://git.kernel.org/stable/c/c4eae7bac880edd88aaed6a8ec2997fa85e259c7
- https://git.kernel.org/stable/c/e3c4e78d636e6dbd8ed72e41b311de2bb7e0b699
- https://git.kernel.org/stable/c/e5e60f17d2462ef5c13db4d1a54eef5778fd2295
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56727.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56727
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
