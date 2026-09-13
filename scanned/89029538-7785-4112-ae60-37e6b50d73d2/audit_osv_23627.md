# [M] ASoC: codecs: wcd934x: Add missing of_node_put() in wcd934x_codec_parse_data

## Summary
Severity: Medium
Advisory: CVE-2022-49239
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49239
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: wcd934x: Add missing of_node_put() in wcd934x_codec_parse_data

The device_node pointer is returned by of_parse_phandle()  with refcount
incremented. We should use of_node_put() on it when done.
This is similar to commit 64b92de9603f
("ASoC: wcd9335: fix a leaked reference by adding missing of_node_put")

## References
- https://git.kernel.org/stable/c/1f24716e38220fc9e52e208d20591d2bc9b7f020
- https://git.kernel.org/stable/c/2f44eca78cc6d4e1779eb95765ec79e433accab4
- https://git.kernel.org/stable/c/9531a631379169d57756b2411178c6238655df88
- https://git.kernel.org/stable/c/f3793eeb7b94a5eeed6f5c7a44bce403c6681a12
- https://git.kernel.org/stable/c/f8e89d84ea83c51ba3ba97ff154f7aa679326760
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49239.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
