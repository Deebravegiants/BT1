# [M] ASoC: mediatek: mt8195: Fix error handling in mt8195_mt6359_rt1019_rt5682_dev_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49240
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49240
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mediatek: mt8195: Fix error handling in mt8195_mt6359_rt1019_rt5682_dev_probe

The device_node pointer is returned by of_parse_phandle()  with refcount
incremented. We should use of_node_put() on it when done.

This function only calls of_node_put() in the regular path.
And it will cause refcount leak in error path.

## References
- https://git.kernel.org/stable/c/c4b7174fe5bb875a09a78674a14a1589d1a672f3
- https://git.kernel.org/stable/c/c652f8f0875b569f8afa80b8cf9762828fd6187b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49240.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49240
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
