# [M] iio: adc: aspeed: Fix refcount leak in aspeed_adc_set_trim_data

## Summary
Severity: Medium
Advisory: CVE-2022-49684
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49684
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: aspeed: Fix refcount leak in aspeed_adc_set_trim_data

of_find_node_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/8a2b6b5687984a010ed094b4f436a2f091987758
- https://git.kernel.org/stable/c/9664491db50a84be92696c8fad2c3b49a7a5f36f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49684.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49684
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
