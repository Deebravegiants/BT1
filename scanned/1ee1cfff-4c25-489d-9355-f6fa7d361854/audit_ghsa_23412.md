# [M] MongoDB Tools Improper Certificate Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6cwm-wm82-hgrw
CVE: CVE-2020-7924
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6cwm-wm82-hgrw
Type: github-advisory

## Affected
- Go: `github.com/mongodb/mongo-tools` — affected >=100.0.0 <100.2.0

## Details
Usage of specific command line parameter in MongoDB Tools which was originally intended to just skip hostname checks, may result in MongoDB skipping all certificate validation. This may result in accepting invalid certificates.This issue affects: MongoDB Inc. MongoDB Database Tools 3.6 versions later than 3.6.5; 3.6 versions prior to 3.6.21; 4.0 versions prior to 4.0.21; 4.2 versions prior to 4.2.11; 100 versions prior to 100.2.0. MongoDB Inc. Mongomirror 0 versions later than 0.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7924
- https://github.com/mongodb/mongo-tools/commit/8c1800b5155084f954a39a1f2f259efac3bb86de
- https://github.com/advisories/GHSA-6cwm-wm82-hgrw
- https://github.com/mongodb/mongo-tools
- https://jira.mongodb.org/browse/TOOLS-2587
