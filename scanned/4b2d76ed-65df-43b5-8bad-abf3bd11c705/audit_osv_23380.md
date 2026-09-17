# [M] sfc/siena: fix null pointer dereference in efx_hard_start_xmit

## Summary
Severity: Medium
Advisory: CVE-2022-48646
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48646
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

sfc/siena: fix null pointer dereference in efx_hard_start_xmit

Like in previous patch for sfc, prevent potential (but unlikely) NULL
pointer dereference.

## References
- https://git.kernel.org/stable/c/589c6eded10c77a12b7b2cf235b6b19a2bdb91fa
- https://git.kernel.org/stable/c/a4eadca702dff0768dd01be6789bbec2a18e5b0a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48646.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48646
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
