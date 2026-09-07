# [H] Vaultwarden vulnerable to user impersonation

## Summary
Severity: High
Advisory: GHSA-x7m9-mv49-fv73
CVE: CVE-2024-55225
CWE: CWE-276, CWE-863
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-01-09
Source: https://github.com/advisories/GHSA-x7m9-mv49-fv73
Type: github-advisory

## Affected
- crates.io: `vaultwarden` — affected >=0 <1.32.5

## Details
An issue in the component src/api/identity.rs of Vaultwarden prior to v1.32.5 allows attackers to impersonate users, including Administrators, via a crafted authorization request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55225
- https://github.com/dani-garcia/vaultwarden/commit/20d9e885bfcd7df7828d92c6e59ed5fe7b40a879
- https://github.com/dani-garcia/vaultwarden/commit/37c14c3c69b244ec50f5c62b4c9260171607c1d8
- https://github.com/dani-garcia/vaultwarden
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.32.4
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.32.5
- https://insinuator.net/2024/11/vulnerability-disclosure-authentication-bypass-in-vaultwarden-versions-1-32-5
