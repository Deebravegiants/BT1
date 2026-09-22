# [C] CVE-2026-16337

## Summary
Severity: Critical
Advisory: CVE-2026-16337
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-16337
Type: osv

## Details
Improper authorization in the ToolGroupResource and RoleAjax REST/DWR endpoints in dotCMS dotCMS 21.02 through 26.06.22-03 on all platforms allows a low-privileged authenticated backend user to self-assign the administrative layout and self-grant the CMS Administrator role, then achieve remote code execution via a crafted OSGi bundle upload whose BundleActivator executes arbitrary shell commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16337.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-16337
- https://github.com/dotCMS/core/pull/36344
