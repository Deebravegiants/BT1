# [M] ASoC: samsung: Fix refcount leak in aries_audio_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49477
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49477
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: samsung: Fix refcount leak in aries_audio_probe

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
If extcon_find_edev_by_node() fails, it doesn't call of_node_put()
Calling of_node_put() after extcon_find_edev_by_node() to fix this.

## References
- https://git.kernel.org/stable/c/46d1b310a2d571811c4e08041ce287babb60b86a
- https://git.kernel.org/stable/c/70130bde3457d28c02c76b6cacc5d40a72dd6e17
- https://git.kernel.org/stable/c/85d899f396622d3034643bf89615a78f9be7c91a
- https://git.kernel.org/stable/c/bf4a9b2467b775717d0e9034ad916888e19713a3
- https://git.kernel.org/stable/c/cacea459f95be22b3750f3b25b7a1c5897a68206
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49477.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49477
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
