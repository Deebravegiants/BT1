# [H] CVE-2023-31483

## Summary
Severity: High
Advisory: CVE-2023-31483
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-04-28
Source: https://osv.dev/vulnerability/CVE-2023-31483
Type: osv

## Details
tar/TarFileReader.cpp in Cauldron cbang before bastet-v8.1.17 has a directory traversal during extraction that allows the attacker to create or write to files outside the current directory via a crafted tar archive.

## References
- https://github.com/CauldronDevelopmentLLC/cbang/compare/bastet-v8.1.16...bastet-v8.1.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31483.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31483
- https://github.com/CauldronDevelopmentLLC/cbang/issues/115
