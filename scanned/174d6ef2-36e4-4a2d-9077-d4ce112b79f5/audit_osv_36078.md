# [M] NoSleep 1.5.1 - Unauthorized disclosure of root-owned files through privileged XPC helper

## Summary
Severity: Medium
Advisory: CVE-2026-19755
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-19755
Type: osv

## Details
NoSleep 1.5.1 exposes a privileged XPC Mach service and accepts raw dictionary messages containing attacker-controlled command and NSBundlePath values.This issue affects NoSleep: 1.5.1.

## References
- https://github.com/integralpro/nosleep/
- https://fluidattacks.com/advisories/iggy
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19755.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19755
- https://github.com/integralpro/nosleep
