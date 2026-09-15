# [M] PCI: endpoint: Fix misused goto label

## Summary
Severity: Medium
Advisory: CVE-2022-49115
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49115
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: endpoint: Fix misused goto label

Fix a misused goto label jump since that can result in a memory leak.

## References
- https://git.kernel.org/stable/c/70236a0d2d62b081d52076de22d8d017d6cbe99f
- https://git.kernel.org/stable/c/7c657c0694ff690e361a13ce41c36b9dfb433ec8
- https://git.kernel.org/stable/c/bf8d87c076f55b8b4dfdb6bc6c6b6dc0c2ccb487
- https://git.kernel.org/stable/c/d3642fc64276b06446290f82fd45630aeaa4b007
- https://git.kernel.org/stable/c/dc9d33b2d8d09e6478e8ef817a81cf26930acc3e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49115.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
