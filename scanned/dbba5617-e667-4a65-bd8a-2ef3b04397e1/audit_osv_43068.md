# [H] octeontx2-af: Validate NIX maximum LFs correctly

## Summary
Severity: High
Advisory: CVE-2026-72410
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72410
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: Validate NIX maximum LFs correctly

NIX maximum number of LFs can be set via devlink command
but that can be done before assigning any LFs to a PF/VF.
The condition used to check whether any LFs are assigned is
incorrect. This patch fixes that condition.

## References
- https://git.kernel.org/stable/c/0933fe0130eb71af0c3ab481b40f543b458a8c54
- https://git.kernel.org/stable/c/1576d12a39860418d6a68b402fda71a48f04a57c
- https://git.kernel.org/stable/c/b1f6381acf9d55fab208e8b4c252a5a671820bd9
- https://git.kernel.org/stable/c/e0ac054416bf4e913fe96cefefe94e3331bbe6fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72410.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72410
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
