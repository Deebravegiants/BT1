# [H] Authentication Bypass by Primary Weakness in github.com/kongchuanhujiao/server

## Summary
Severity: High
Advisory: GHSA-8wrg-m8vm-5fvj
CVE: CVE-2021-21403
CWE: CWE-287, CWE-305
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-8wrg-m8vm-5fvj
Type: github-advisory

## Affected
- Go: `github.com/kongchuanhujiao/server` — affected >=0 <1.3.21

## Details
### Impact

Authentication Bypass by Primary Weakness (CWE-305)

Commit:

https://github.com/kongchuanhujiao/server/commit/9a125624f219e496bdf4b07b404816d5a309bdc1

ALL Users  is impacted.

### Patches

Yes, PLEASE UPGRADE TO v1.3.21-beta.d0ffc0a6

## References
- https://github.com/kongchuanhujiao/server/security/advisories/GHSA-8wrg-m8vm-5fvj
- https://nvd.nist.gov/vuln/detail/CVE-2021-21403
- https://github.com/kongchuanhujiao/server/commit/9a125624f219e496bdf4b07b404816d5a309bdc1
