# [C] Origin Validation Error in rdiffweb

## Summary
Severity: Critical
Advisory: GHSA-824x-jcxf-hpfg
CVE: CVE-2022-3457
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-14
Source: https://github.com/advisories/GHSA-824x-jcxf-hpfg
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.0a5

## Details
ikus060/rdiffweb prior to 2.5.0a5 did not enforce origin validation in web traffic. Users are advised to upgrade to version 2.5.0a5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3457
- https://github.com/ikus060/rdiffweb/commit/afc1bdfab5161c74012ff2590a6ec49cc0d8fde0
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Origin
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-43161.yaml
- https://huntr.dev/bounties/cfcab02e-d6ad-4dcf-b1b0-da90434bc55b
