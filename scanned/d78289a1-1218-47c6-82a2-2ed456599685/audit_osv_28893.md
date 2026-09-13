# [H] CVE-2024-37391

## Summary
Severity: High
Advisory: CVE-2024-37391
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-22
Source: https://osv.dev/vulnerability/CVE-2024-37391
Type: osv

## Details
ProtonVPN before 3.2.10 on Windows mishandles the drive installer path, which should use this: '"' + ExpandConstant('{autopf}\Proton\Drive') + '"' in Setup/setup.iss.

## References
- https://github.com/ProtonVPN/win-app/compare/3.2.9...3.2.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37391.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37391
- https://github.com/ProtonVPN/win-app/commit/2e4e25036842aaf48838c6a59f14671b86c20aa7
