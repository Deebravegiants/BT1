# [H] i40e: fix input validation logic for action_meta

## Summary
Severity: High
Advisory: CVE-2025-39970
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39970
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: fix input validation logic for action_meta

Fix condition to check 'greater or equal' to prevent OOB dereference.

## References
- https://git.kernel.org/stable/c/28465770ca3b694286ff9ed6dfd558413f57d98f
- https://git.kernel.org/stable/c/3118f41d8fa57b005f53ec3db2ba5eab1d7ba12b
- https://git.kernel.org/stable/c/3883e9702b6a4945e93b16c070f338a9f5b496f9
- https://git.kernel.org/stable/c/461e0917eedcd159d87f3ea846754a1e07d7e78a
- https://git.kernel.org/stable/c/560e1683410585fbd5df847f43433c4296f0d222
- https://git.kernel.org/stable/c/9739d5830497812b0bdeaee356ddefbe60830b88
- https://git.kernel.org/stable/c/a88c1b2746eccf00e2094b187945f0f1e990b400
- https://git.kernel.org/stable/c/f8c8e11825b24661596fa8db2f0981ba17ed0817
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39970.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39970
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
