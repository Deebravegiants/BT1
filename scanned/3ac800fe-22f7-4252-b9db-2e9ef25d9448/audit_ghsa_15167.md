# [M] Apprite CLI makes Use of Hard-coded Credentials

## Summary
Severity: Medium
Advisory: GHSA-g777-crp9-m27g
CVE: CVE-2023-50974
CWE: CWE-798
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-g777-crp9-m27g
Type: github-advisory

## Affected
- npm: `appwrite-cli` — affected >=0 <3.0.0
- PyPI: `appwrite` — affected >=0 <3.0.0

## Details
In Appwrite CLI before 3.0.0, when using the login command, the credentials of the Appwrite user are stored in a ~/.appwrite/prefs.json file with 0644 as UNIX permissions. Any user of the local system can access those credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50974
- https://appwrite.io/docs/tooling/command-line/installation
- https://gist.github.com/SkypLabs/72ee00ecfa7d1a3494e2d69a24279c1d
- https://github.com/appwrite/sdk-for-cli
- https://github.com/pypa/advisory-database/tree/main/vulns/appwrite/PYSEC-2024-2.yaml
