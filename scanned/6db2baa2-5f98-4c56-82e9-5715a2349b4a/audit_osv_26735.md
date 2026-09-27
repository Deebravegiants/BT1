# [H] soc: qcom: qmi_encdec: Restrict string length in decode

## Summary
Severity: High
Advisory: CVE-2023-53729
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53729
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: qcom: qmi_encdec: Restrict string length in decode

The QMI TLV value for strings in a lot of qmi element info structures
account for null terminated strings with MAX_LEN + 1. If a string is
actually MAX_LEN + 1 length, this will cause an out of bounds access
when the NULL character is appended in decoding.

## References
- https://git.kernel.org/stable/c/22ee7c9c7f381be178b4457bc54530002e08e938
- https://git.kernel.org/stable/c/2ccab9f82772ead618689d17dbc6950d6bd1e741
- https://git.kernel.org/stable/c/64c5e916fabe5ef7bef0210b8a59fa8941ee1b8e
- https://git.kernel.org/stable/c/6b58859e7c4ac357517a59f0801e8ce1b58a8ee2
- https://git.kernel.org/stable/c/8d207400fd6b79c92aeb2f33bb79f62dff904ea2
- https://git.kernel.org/stable/c/b2f39b813d1eed4a522428d1e6acd7dfe9b81579
- https://git.kernel.org/stable/c/f6250ecb7fbb934b89539e7e2ba6c1d8555c0975
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53729.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53729
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
