# [M] Cross-site Scripting in CKAN

## Summary
Severity: Medium
Advisory: GHSA-6w9p-88qg-p3g3
CVE: CVE-2021-25967
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-03
Source: https://github.com/advisories/GHSA-6w9p-88qg-p3g3
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=2.9.0 <2.10.0

## Details
In CKAN, versions 2.9.0 to 2.9.3 are affected by a stored XSS vulnerability via SVG file upload of users’ profile picture. This allows low privileged application users to store malicious scripts in their profile picture. These scripts are executed in a victim’s browser when they open the malicious profile picture

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25967
- https://github.com/ckan/ckan/pull/6477
- https://github.com/ckan/ckan/commit/5a46989c0a4f2c2873ca182c196da83b82babd25
- https://github.com/advisories/GHSA-6w9p-88qg-p3g3
- https://github.com/ckan/ckan
- https://github.com/pypa/advisory-database/tree/main/vulns/ckan/PYSEC-2021-841.yaml
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25967
