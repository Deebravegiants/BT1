# [H] memory: tegra20-emc: fix an OF node reference bug in tegra_emc_find_node_by_ram_code()

## Summary
Severity: High
Advisory: CVE-2024-58034
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58034
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

memory: tegra20-emc: fix an OF node reference bug in tegra_emc_find_node_by_ram_code()

As of_find_node_by_name() release the reference of the argument device
node, tegra_emc_find_node_by_ram_code() releases some device nodes while
still in use, resulting in possible UAFs. According to the bindings and
the in-tree DTS files, the "emc-tables" node is always device's child
node with the property "nvidia,use-ram-code", and the "lpddr2" node is a
child of the "emc-tables" node. Thus utilize the
for_each_child_of_node() macro and of_get_child_by_name() instead of
of_find_node_by_name() to simplify the code.

This bug was found by an experimental verification tool that I am
developing.

[krzysztof: applied v1, adjust the commit msg to incorporate v2 parts]

## References
- https://git.kernel.org/stable/c/3b02273446e23961d910b50cc12528faec649fb2
- https://git.kernel.org/stable/c/755e44538c190c31de9090d8e8821d228fcfd416
- https://git.kernel.org/stable/c/b9784e5cde1f9fb83661a70e580e381ae1264d12
- https://git.kernel.org/stable/c/c144423cb07e4e227a8572d5742ca2b36ada770d
- https://git.kernel.org/stable/c/c3def10c610ae046aaa61d00528e7bd15e4ad8d3
- https://git.kernel.org/stable/c/e9d07e91de140679eeaf275f47ad154467cb9e05
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58034.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58034
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
