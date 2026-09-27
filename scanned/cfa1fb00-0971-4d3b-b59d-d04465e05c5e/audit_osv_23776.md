# [M] ASoC: ti: j721e-evm: Fix refcount leak in j721e_soc_probe_*

## Summary
Severity: Medium
Advisory: CVE-2022-49473
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49473
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: ti: j721e-evm: Fix refcount leak in j721e_soc_probe_*

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not needed anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/2a3966b950b37a6f10c5f9caee15b4cdcf5a7413
- https://git.kernel.org/stable/c/510e879420b410d88c612aecc6ca15dc6fe77473
- https://git.kernel.org/stable/c/554df0f70bff1ace6d2df2fcaddbc9b7bd509de2
- https://git.kernel.org/stable/c/a34840c4eb3278a7c29c9c57a65ce7541c66f9f2
- https://git.kernel.org/stable/c/d748ff8fbb3a5296bddd586445dc692b079cbe3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49473.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49473
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
