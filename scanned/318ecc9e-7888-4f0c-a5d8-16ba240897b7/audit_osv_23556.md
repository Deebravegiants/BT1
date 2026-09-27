# [M] mips: ralink: fix a refcount leak in ill_acc_of_setup()

## Summary
Severity: Medium
Advisory: CVE-2022-49117
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49117
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mips: ralink: fix a refcount leak in ill_acc_of_setup()

of_node_put(np) needs to be called when pdev == NULL.

## References
- https://git.kernel.org/stable/c/060a485df4ec1183d543317511cb4caa43468b5d
- https://git.kernel.org/stable/c/142ae7d4f21524acfe073e5a3da5667aa85eb970
- https://git.kernel.org/stable/c/4a0a1436053b17e50b7c88858fb0824326641793
- https://git.kernel.org/stable/c/5fb47ca3490813d3884d8ad0b2ce511aa3537551
- https://git.kernel.org/stable/c/8d7f7ef7980f287ace1c15f2ac03d6754e12f071
- https://git.kernel.org/stable/c/c74c755daed551b9aceb8388159180861474bdfe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49117.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
