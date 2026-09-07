# [H] pretix Stored Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-45rp-q25w-4426
CVE: CVE-2024-8113
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:U/V:X/RE:L/U:Green (CVSS_V4)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-45rp-q25w-4426
Type: github-advisory

## Affected
- PyPI: `pretix` — affected >=0 <2024.7.1

## Details
Stored XSS in organizer and event settings of pretix up to 2024.7.0 allows malicious event organizers to inject HTML tags into e-mail previews on settings page. The default Content Security Policy of pretix prevents execution of attacker-provided scripts, making exploitation unlikely. However, combined with a CSP bypass (which is not currently known) the vulnerability could be used to impersonate other organizers or staff users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8113
- https://github.com/pretix/pretix/commit/0f44a2ad4e170882dbe6b9d95dba6c36e4e181cf
- https://github.com/pretix/pretix
- https://github.com/pypa/advisory-database/tree/main/vulns/pretix/PYSEC-2024-180.yaml
- https://pretix.eu/about/en/blog/20240823-release-2024-7-1
