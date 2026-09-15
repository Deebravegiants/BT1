# [H] firmware: arm_scmi: Fix OOB in scmi_power_name_get()

## Summary
Severity: High
Advisory: CVE-2026-80649
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80649
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_scmi: Fix OOB in scmi_power_name_get()

scmi_power_name_get() does not validate the domain number passed by the
external caller, which may lead to an out-of-bounds access.

Fix this by returning "unknown" for invalid domains, like
scmi_reset_name_get() does.

## References
- https://git.kernel.org/stable/c/01613f5e4ff6c080260615392338e92e261d109b
- https://git.kernel.org/stable/c/0db2bb3c948ef8b7364768554d6ab5e1544dc441
- https://git.kernel.org/stable/c/11bb771f3c55b4cef3879e69da4ddecd6085569c
- https://git.kernel.org/stable/c/11daac2817dca75e3eabb2050bc620c29e686fcd
- https://git.kernel.org/stable/c/30aa348494531adfb043b2e883afc0439e5fcdca
- https://git.kernel.org/stable/c/ca94597440fa546e56293abe9d0af6c73535d44e
- https://git.kernel.org/stable/c/f9ef3f66f4b18078e464b7606f9497e4dbeb9905
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80649.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80649
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
