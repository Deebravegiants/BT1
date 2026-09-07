# [H] Rembg CORS misconfiguration

## Summary
Severity: High
Advisory: GHSA-59qh-fmm7-3g9q
CVE: CVE-2025-25302
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-59qh-fmm7-3g9q
Type: github-advisory

## Affected
- PyPI: `rembg` — affected >=0

## Details
Rembg is a tool to remove images background. In Rembg 2.0.57 and earlier, the CORS middleware is setup incorrectly. All origins are reflected, which allows any website to send cross site requests to the rembg server and thus query any API. Even if authentication were to be enabled, allow_credentials is set to True, which would allow any website to send authenticated cross site requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25302
- https://github.com/danielgatis/rembg
- https://github.com/danielgatis/rembg/blob/d1e00734f8a996abf512a3a5c251c7a9a392c90a/rembg/commands/s_command.py#L93
- https://securitylab.github.com/advisories/GHSL-2024-161_GHSL-2024-162_rembg
