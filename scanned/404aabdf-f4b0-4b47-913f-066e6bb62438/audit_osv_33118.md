# [H] media: usbtv: Lock resolution while streaming

## Summary
Severity: High
Advisory: CVE-2025-39714
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39714
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: usbtv: Lock resolution while streaming

When an program is streaming (ffplay) and another program (qv4l2)
changes the TV standard from NTSC to PAL, the kernel crashes due to trying
to copy to unmapped memory.

Changing from NTSC to PAL increases the resolution in the usbtv struct,
but the video plane buffer isn't adjusted, so it overflows.

[hverkuil: call vb2_is_busy instead of vb2_is_streaming]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/3d83d0b5ae5045a7a246ed116b5f6c688a12f9e9
- https://git.kernel.org/stable/c/5427dda195d6baf23028196fd55a0c90f66ffa61
- https://git.kernel.org/stable/c/7e40e0bb778907b2441bff68d73c3eb6b6cd319f
- https://git.kernel.org/stable/c/9f886d21e235c4bd038cb20f6696084304197ab3
- https://git.kernel.org/stable/c/c35e7c7a004ef379a1ae7c7486d4829419acad1d
- https://git.kernel.org/stable/c/c3d75524e10021aa5c223d94da4996640aed46c0
- https://git.kernel.org/stable/c/ee7bade8b9244834229b12b6e1e724939bedd484
- https://git.kernel.org/stable/c/ef9b3c22405192afaa279077ddd45a51db90b83d
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39714.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39714
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
