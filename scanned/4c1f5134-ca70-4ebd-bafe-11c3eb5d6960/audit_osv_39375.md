# [C] Dokku: Arbitrary File Write via Tar Symlink Traversal in git:from-archive and certs:add

## Summary
Severity: Critical
Advisory: CVE-2026-45405
Aliases: GHSA-j6qq-xg73-ghqg
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-45405
Type: osv

## Details
Dokku is a docker-powered PaaS. Prior to 0.38.2, the git:from-archive and certs:add commands extract user-supplied tar/zip archives into temporary directories without sanitizing member paths or preventing symlink traversal. GNU tar creates symlinks during extraction and follows them for subsequent entries, allowing an attacker to write arbitrary files anywhere writable by the dokku user — including overwriting ~/.ssh/authorized_keys to gain unrestricted shell access. This vulnerability is fixed in 0.38.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45405.json
- https://github.com/dokku/dokku/security/advisories/GHSA-j6qq-xg73-ghqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-45405
- https://github.com/dokku/dokku/pull/8591
