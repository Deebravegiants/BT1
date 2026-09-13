# [H] zrok copy writes attacker-controlled WebDAV paths outside the destination root

## Summary
Severity: High
Advisory: GHSA-c656-jcx2-7pqj
CVE: CVE-2026-45576
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-c656-jcx2-7pqj
Type: github-advisory

## Affected
- Go: `github.com/openziti/zrok/v2` — affected >=0 <2.0.3
- Go: `github.com/openziti/zrok` — affected >=0.4.23

## Details
## Summary

Alice runs `zrok2 copy` from a WebDAV or zrok drive controlled by Bob into a local filesystem target. Bob returns a DAV `href` such as `/../outside.txt`. The sync pipeline stores that path in the source inventory and passes it to `FilesystemTarget.WriteStream`, which joins it with the target root and creates the file outside Alice's selected directory.

### Impact
Users given access to a zrok share may be able to traverse the directory tree arbitrarily with the sharing users credentials, allowing for sensitive information to be overwritten.

## References
- https://github.com/openziti/zrok/security/advisories/GHSA-c656-jcx2-7pqj
- https://github.com/openziti/zrok
