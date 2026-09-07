# [C] Deserialization of Untrusted Data in thinkphp

## Summary
Severity: Critical
Advisory: GHSA-j2h2-g882-x9j2
CVE: CVE-2022-45982
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-j2h2-g882-x9j2
Type: github-advisory

## Affected
- Packagist: `topthink/think` — affected >=0

## Details
thinkphp 6.0.0~6.0.13 and 6.1.0~6.1.1 contains a deserialization vulnerability. This vulnerability allows attackers to execute arbitrary code via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45982
- https://gist.github.com/Dar1in9s/aa87df679057db3bbdade360d77f8cca
- https://github.com/top-think/think
