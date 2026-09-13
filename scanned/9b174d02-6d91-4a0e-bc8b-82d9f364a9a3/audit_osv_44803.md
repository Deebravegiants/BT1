# [C] Lara Dashboard before 1.3.2 Missing Authorization in Marketplace Module Install Action

## Summary
Severity: Critical
Advisory: CVE-2026-86438
Aliases: GHSA-4x9p-vg5m-vr6p
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86438
Type: osv

## Details
Lara Dashboard before 1.3.2 fails to authorize the MarketplaceModuleBrowser installModule Livewire action, allowing non-Superadmin administrators to install modules. Attackers can download and auto-activate arbitrary PHP modules from the marketplace over unsigned HTTP requests, achieving remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86438.json
- https://github.com/laradashboard/laradashboard/releases/tag/v1.3.2
- https://github.com/laradashboard/laradashboard/security/advisories/GHSA-4x9p-vg5m-vr6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-86438
- https://www.vulncheck.com/advisories/lara-dashboard-before-1.3.2-missing-authorization-in-marketplace-module-install-action
- https://github.com/laradashboard/laradashboard/commit/738cc1a219ce459323ef1d09c3789075f1b8d2f2
- https://github.com/laradashboard/laradashboard
- https://github.com/laradashboard/laradashboard/blob/v1.3.1/app/Livewire/Marketplace/MarketplaceModuleBrowser.php#L76-L120
- https://github.com/laradashboard/laradashboard/blob/v1.3.1/app/Policies/ModulePolicy.php#L32-L38
