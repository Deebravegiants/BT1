# [H] rsync < 3.5.0 TOCTOU Race Condition Directory Escape via rrsync

## Summary
Severity: High
Advisory: CVE-2026-53783
Aliases: GHSA-9cgc-64g4-3gv5
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53783
Type: osv

## Details
rsync before 3.5.0 contains a time-of-check to time-of-use (TOCTOU) race condition vulnerability in the rrsync restricted shell wrapper that allows authenticated clients to escape enforced directory restrictions by substituting a symlink for a path component after validation but before transfer processing. Attackers can additionally leverage unrestricted flags such as --copy-unsafe-links, -D, and --log-file through rrsync to read or write files outside the permitted directory subtree.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53783.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-9cgc-64g4-3gv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53783
- https://www.vulncheck.com/advisories/rsync-toctou-race-condition-directory-escape-via-rrsync
- https://github.com/RsyncProject/rsync
