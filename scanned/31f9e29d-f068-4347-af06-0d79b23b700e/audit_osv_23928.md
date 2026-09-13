# [M] iio: adc: adi-axi-adc: Fix refcount leak in adi_axi_adc_attach_client

## Summary
Severity: Medium
Advisory: CVE-2022-49683
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49683
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: adi-axi-adc: Fix refcount leak in adi_axi_adc_attach_client

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/501652a2ad5450b4908e1f204ce75b2414c305b7
- https://git.kernel.org/stable/c/5eaa84e1605035a90a64d25b6cba79e89d188175
- https://git.kernel.org/stable/c/ab7bf025cee89db73c649216ddd2bc589c3d3862
- https://git.kernel.org/stable/c/ada7b0c0dedafd7d059115adf49e48acba3153a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49683.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
