# [M] DbGate allows for File Traversal via file parameter

## Summary
Severity: Medium
Advisory: CVE-2025-50184
Aliases: GHSA-2fp9-29gv-p5gm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2025-07-26
Source: https://osv.dev/vulnerability/CVE-2025-50184
Type: osv

## Details
DbGate is cross-platform database manager. In versions 6.4.3-premium-beta.5 and below, DbGate is vulnerable to a directory traversal flaw. The file parameter is not properly restricted to the intended uploads directory. As a result, the endpoint that lists files within the upload directory can be manipulated to access arbitrary files on the system. By supplying a crafted path to the file parameter, an attacker can read files outside the upload directory, potentially exposing sensitive system-level data. This is fixed in version 6.4.3-beta.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50184.json
- https://github.com/dbgate/dbgate/security/advisories/GHSA-2fp9-29gv-p5gm
- https://nvd.nist.gov/vuln/detail/CVE-2025-50184
- https://github.com/dbgate/dbgate/commit/18b11df672b5a887bc17a6b9fdd13f9742c8f98e
