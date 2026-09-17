# [H] Malicious client can bypass destination directory validation on local sources upload

## Summary
Severity: High
Advisory: CVE-2026-15789
Aliases: CVE-2026-75593, GHSA-g2h8-426c-7976
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-15789
Type: osv

## Details
A custom client can produce such an upload request to the BuildKit daemon that files can escape from the BuildKit-controlled state directory. The client needs to have valid permissions to access the BuildKit control API to issue builds, e.g., bypass authentication, etc.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15789.json
- https://github.com/moby/buildkit/security/advisories/GHSA-g2h8-426c-7976
- https://nvd.nist.gov/vuln/detail/CVE-2026-15789
