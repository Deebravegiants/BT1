# [H] media: imx-jpeg: Align upwards buffer size

## Summary
Severity: High
Advisory: CVE-2022-50182
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50182
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: imx-jpeg: Align upwards buffer size

The hardware can support any image size WxH,
with arbitrary W (image width) and H (image height) dimensions.

Align upwards buffer size for both encoder and decoder.
and leave the picture resolution unchanged.

For decoder, the risk of memory out of bounds can be avoided.
For both encoder and decoder, the driver will lift the limitation of
resolution alignment.

For example, the decoder can support jpeg whose resolution is 227x149
the encoder can support nv12 1080P, won't change it to 1920x1072.

## References
- https://git.kernel.org/stable/c/447795ffb17cd60bb544e0abfc9399e180a14a2f
- https://git.kernel.org/stable/c/73d1836ed7911953182b787745cb8c5857a2661c
- https://git.kernel.org/stable/c/9ae2d729de6350c53a06c57782751d84eb2c08d9
- https://git.kernel.org/stable/c/9e7aa76cdb02923ee23a0ddd48f38bdc3512f92b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50182.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50182
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
