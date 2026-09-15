# [C] rdiffweb vulnerable to Improper Restriction of Rendered UI Layers or Frames

## Summary
Severity: Critical
Advisory: GHSA-m379-x4xc-38x9
CVE: CVE-2022-3167
CWE: CWE-1021
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-09
Source: https://github.com/advisories/GHSA-m379-x4xc-38x9
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.1

## Details
rdiffweb prior to 2.4.1 is vulnerable to Improper Restriction of Rendered UI Layers or Frames. This allows attackers to perform clickjacking attacks that can trick victims into performing actions such as entering passwords, liking or deleting posts, and/or initiating an account deletion. This issue has been patched in version 2.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3167
- https://github.com/ikus060/rdiffweb/commit/7294bb7466532762c93d711211e5958940c1b428
- https://github.com/advisories/GHSA-m379-x4xc-38x9
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-268.yaml
- https://huntr.dev/bounties/e5c2625b-34cc-4805-8223-80f2689e4e5c
