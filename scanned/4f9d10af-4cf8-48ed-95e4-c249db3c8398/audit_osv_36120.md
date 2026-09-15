# [M] eopkg has Path Traversal: '../filedir' vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-21436
Aliases: GHSA-786v-47cq-qm6m
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:A/VC:N/VI:H/VA:N/SC:N/SI:H/SA:H)
Published: 2026-01-01
Source: https://osv.dev/vulnerability/CVE-2026-21436
Type: osv

## Details
eopkg is a Solus package manager implemented in python3. In versions prior to 4.4.0, a malicious package could escape the directory set by `--destdir`. This requires the installation of a package from a malicious or compromised source. Files in such packages would not be installed in the path given by `--destdir`, but on a different location on the host. The issue has been fixed in v4.4.0. Users only installing packages from the Solus repositories are not affected.

## References
- https://github.com/getsolus/eopkg/releases/tag/v4.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21436.json
- https://github.com/getsolus/eopkg/security/advisories/GHSA-786v-47cq-qm6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-21436
- https://github.com/getsolus/eopkg/commit/e7694323ed64e08b5b4b108fff273c64125cd39d
- https://github.com/getsolus/eopkg/pull/201
