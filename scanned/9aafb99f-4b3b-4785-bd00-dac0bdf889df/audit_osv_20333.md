# [H] CVE-2021-32814

## Summary
Severity: High
Advisory: CVE-2021-32814
Aliases: GHSA-2hj9-cxmc-m4g7
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-08-03
Source: https://osv.dev/vulnerability/CVE-2021-32814
Type: osv

## Details
Skytable is a NoSQL database with automated snapshots and TLS. Versions prior to 0.5.1 are vulnerable to a a directory traversal attack enabling remotely connected clients to destroy and/or manipulate critical files on the host's file system. This security bug has been patched in version 0.5.1. There are no known workarounds aside from upgrading.

## References
- https://github.com/skytable/skytable/blob/next/CHANGELOG.md#version-051-2021-03-17
- https://github.com/skytable/skytable/security/advisories/GHSA-2hj9-cxmc-m4g7
- https://github.com/skytable/skytable/commit/38b011273bb92b83c61053ae2fcd80aa9320315c#diff-1cdcf1a793c71ec658782437e4da7e3a37042bc1e2c12545942e9a14679c4b7e
- https://security.skytable.io/ve/s/00001.html
