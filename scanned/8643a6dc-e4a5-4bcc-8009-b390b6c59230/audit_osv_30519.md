# [H] media: uvcvideo: Skip parsing frames of type UVC_VS_UNDEFINED in uvc_parse_format

## Summary
Severity: High
Advisory: CVE-2024-53104
Aliases: A-378455392, ASB-A-378455392
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53104
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8, >=6.12.0 <6.12.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: uvcvideo: Skip parsing frames of type UVC_VS_UNDEFINED in uvc_parse_format

This can lead to out of bounds writes since frames of this type were not
taken into account when calculating the size of the frames buffer in
uvc_parse_streaming.

## References
- https://git.kernel.org/stable/c/1ee9d9122801eb688783acd07791f2906b87cb4f
- https://git.kernel.org/stable/c/467d84dc78c9abf6b217ada22b3fdba336262e29
- https://git.kernel.org/stable/c/575a562f7a3ec2d54ff77ab6810e3fbceef2a91d
- https://git.kernel.org/stable/c/622ad10aae5f5e03b7927ea95f7f32812f692bb5
- https://git.kernel.org/stable/c/684022f81f128338fe3587ec967459669a1204ae
- https://git.kernel.org/stable/c/95edf13a48e75dc2cc5b0bc57bf90d6948a22fe8
- https://git.kernel.org/stable/c/beced2cb09b58c1243733f374c560a55382003d6
- https://git.kernel.org/stable/c/ecf2b43018da9579842c774b7f35dbe11b5c38dd
- https://git.kernel.org/stable/c/faff5bbb2762c44ec7426037b3000e77a11d6773
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-53104
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53104.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53104
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
