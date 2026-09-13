# [M] Panda3D <= 1.10.16 Deploy-Stub Stack Exhaustion via Unbounded alloca()

## Summary
Severity: Medium
Advisory: CVE-2026-22188
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-22188
Type: osv

## Details
The deploy-stub component in Panda3D versions up to and including 1.10.16 contains a denial of service vulnerability due to unbounded stack allocation. The deploy-stub executable allocates argv_copy and argv_copy2 using alloca() based directly on the attacker-controlled argc value without validation. Supplying a large number of command-line arguments can exhaust stack space and propagate uninitialized stack memory into Python interpreter initialization, resulting in a reliable crash and undefined behavior.

## References
- https://www.panda3d.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22188.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22188
- https://www.vulncheck.com/advisories/panda3d-deploy-stub-stack-exhaustion-via-unbounded-alloca
- https://github.com/panda3d/panda3d
- https://seclists.org/fulldisclosure/2026/Jan/9
