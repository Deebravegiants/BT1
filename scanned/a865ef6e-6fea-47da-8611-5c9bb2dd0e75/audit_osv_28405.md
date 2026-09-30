# [M] Git Credential Manager (GCM)'s Debian package does not set root ownership on installed files

## Summary
Severity: Medium
Advisory: CVE-2024-32478
Aliases: GHSA-3c3g-h9rx-f7vq
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2024-32478
Type: osv

## Details
Git Credential Manager (GCM) is a secure Git credential helper. Prior to 2.5.0, the Debian package does not set root ownership on installed files. This allows user 1001 on a multi-user system can replace binary and gain other users' privileges. This vulnerability is fixed in 2.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32478.json
- https://github.com/git-ecosystem/git-credential-manager/security/advisories/GHSA-3c3g-h9rx-f7vq
- https://nvd.nist.gov/vuln/detail/CVE-2024-32478
- https://github.com/git-ecosystem/git-credential-manager/commit/d9ac33c5b1478383672b4425f5ecf875a62efba9
