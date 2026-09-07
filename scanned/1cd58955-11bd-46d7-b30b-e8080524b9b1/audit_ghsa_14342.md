# [M] Modoboa has Weak Password Requirements

## Summary
Severity: Medium
Advisory: GHSA-9gxx-32p7-ff7m
CVE: CVE-2023-2160
CWE: CWE-521
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-04-18
Source: https://github.com/advisories/GHSA-9gxx-32p7-ff7m
Type: github-advisory

## Affected
- PyPI: `modoboa` — affected >=0 <2.1.0

## Details
Modoboa 2.0.5 and prior allows users to set unsafe passwords, such as `1` or `HACK`. This issue is fixed in commit 130257c96a2392ada795785a91178e656e27015c and is part of version 2.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2160
- https://github.com/modoboa/modoboa/commit/130257c96a2392ada795785a91178e656e27015c
- https://github.com/modoboa/modoboa
- https://github.com/pypa/advisory-database/tree/main/vulns/modoboa/PYSEC-2023-34.yaml
- https://huntr.dev/bounties/54fb6d6a-6b39-45b6-b62a-930260ba484b
