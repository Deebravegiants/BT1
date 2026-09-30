# [M] Dokku: Git Credentials in .netrc Stored World-Readable Due to Premature touch

## Summary
Severity: Medium
Advisory: CVE-2026-45407
Aliases: GHSA-xh7p-9crg-pchr
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-45407
Type: osv

## Details
Dokku is a docker-powered PaaS. Prior to 0.38.2, the git:auth command creates $DOKKU_ROOT/.netrc using bash's touch command, which applies the default umask of 0644. This pre-creation defeats the netrc binary's built-in 0600 permission setting, leaving git credentials readable by any local user who can traverse the dokku home directory. This vulnerability is fixed in 0.38.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45407.json
- https://github.com/dokku/dokku/security/advisories/GHSA-xh7p-9crg-pchr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45407
- https://github.com/dokku/dokku/pull/8589
