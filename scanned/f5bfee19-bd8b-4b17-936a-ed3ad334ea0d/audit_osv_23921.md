# [M] memory: samsung: exynos5422-dmc: Fix refcount leak in of_get_dram_timings

## Summary
Severity: Medium
Advisory: CVE-2022-49676
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49676
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

memory: samsung: exynos5422-dmc: Fix refcount leak in of_get_dram_timings

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
This function doesn't call of_node_put() in some error paths.
To unify the structure, Add put_node label and goto it on errors.

## References
- https://git.kernel.org/stable/c/1332661e09304b7b8e84e5edc11811ba08d12abe
- https://git.kernel.org/stable/c/889aad2203e09eed2071ca8985c25e9d6aea5735
- https://git.kernel.org/stable/c/bb2a481778c60f912c363e271ae46b55ff8132db
- https://git.kernel.org/stable/c/cde4480b5ab06195b9164184b0c02ced71e601b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49676.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49676
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
