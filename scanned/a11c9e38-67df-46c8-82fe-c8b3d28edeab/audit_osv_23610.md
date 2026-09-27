# [M] ath10k: Fix error handling in ath10k_setup_msa_resources

## Summary
Severity: Medium
Advisory: CVE-2022-49213
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49213
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ath10k: Fix error handling in ath10k_setup_msa_resources

The device_node pointer is returned by of_parse_phandle() with refcount
incremented. We should use of_node_put() on it when done.

This function only calls of_node_put() in the regular path.
And it will cause refcount leak in error path.

## References
- https://git.kernel.org/stable/c/315772133a4b960859e4f5efe0e738e347188cdc
- https://git.kernel.org/stable/c/32939187f254171a5666badc058bc3787fe454af
- https://git.kernel.org/stable/c/4ed37d611ea5d222c3ecb3549e4c2d34b8f3c335
- https://git.kernel.org/stable/c/74b1d41e1b6410eed5c76d00eedb262036e9eff5
- https://git.kernel.org/stable/c/9747a78d5f758a5284751a10aee13c30d02bd5f1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49213.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49213
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
