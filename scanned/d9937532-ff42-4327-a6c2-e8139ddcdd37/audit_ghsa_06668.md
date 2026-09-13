# [M] SFTPGo has path confinement bypass in public browsable share partial ZIP download

## Summary
Severity: Medium
Advisory: GHSA-h64p-8h4r-6gfh
CVE: CVE-2026-49244
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-h64p-8h4r-6gfh
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=2.2.0 <2.7.3

## Details
## Summary

The public web-client endpoint for partial ZIP downloads of a browsable share did not correctly confine the client-supplied files entries to the shared directory. A requester able to reach a public share could read files located outside the shared directory, as long as the target's canonical path begins with the shared directory's name.

## Patches

Fixed in v2.7.3. The fix replaces the raw prefix check with a directory-boundary–aware check.

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-h64p-8h4r-6gfh
- https://github.com/drakkan/sftpgo
