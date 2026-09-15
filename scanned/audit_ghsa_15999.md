# [H] Adguard Home arbitrary file read vulnerability

## Summary
Severity: High
Advisory: GHSA-9cp9-8gw2-8v7m
CVE: CVE-2024-36814
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-9cp9-8gw2-8v7m
Type: github-advisory

## Affected
- Go: `github.com/AdguardTeam/AdGuardHome` — affected >=0 <0.107.53

## Details
An arbitrary file read vulnerability in Adguard Home before v0.107.52 allows authenticated attackers to access arbitrary files as root on the underlying Operating System via placing a crafted file into a readable directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36814
- https://github.com/AdguardTeam/AdGuardHome/commit/e8fd4b187287a562cbe9018999e5ea576b4c7d68
- https://github.com/AdguardTeam/AdGuardHome
- https://github.com/AdguardTeam/AdGuardHome/blob/7c002e1a99b9b4e4a40e8c66851eda33e666d52d/internal/filtering/http.go#L23C1-L51C2
- https://github.com/AdguardTeam/AdGuardHome/releases/tag/v0.107.53
- https://github.com/itz-d0dgy
- https://happy-little-accidents.pages.dev/posts/CVE-2024-36814
- https://pkg.go.dev/vuln/GO-2024-3184
