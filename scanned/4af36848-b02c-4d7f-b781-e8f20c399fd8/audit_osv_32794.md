# [H] ASoC: qcom: Fix sc7280 lpass potential buffer overflow

## Summary
Severity: High
Advisory: CVE-2025-37979
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37979
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.136, >=6.2.0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: qcom: Fix sc7280 lpass potential buffer overflow

Case values introduced in commit
5f78e1fb7a3e ("ASoC: qcom: Add driver support for audioreach solution")
cause out of bounds access in arrays of sc7280 driver data (e.g. in case
of RX_CODEC_DMA_RX_0 in sc7280_snd_hw_params()).

Redefine LPASS_MAX_PORTS to consider the maximum possible port id for
q6dsp as sc7280 driver utilizes some of those values.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/a12c14577882b1f2b4cff0f86265682f16e97b0c
- https://git.kernel.org/stable/c/a31a4934b31faea76e735bab17e63d02fcd8e029
- https://git.kernel.org/stable/c/b807b7c81a6d066757a94af7b8fa5b6a37e4d0b3
- https://git.kernel.org/stable/c/c0ce01e0ff8a0d61a7b089ab309cdc12bc527c39
- https://git.kernel.org/stable/c/d78888853eb53f47ae16cf3aa5d0444d0331b9f8
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37979.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37979
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
