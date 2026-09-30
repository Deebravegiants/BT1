# [C] Grav CMS before 2.0.16 Symlink Following via createLockFile

## Summary
Severity: Critical
Advisory: CVE-2026-72696
Aliases: GHSA-q8w8-6cq5-j4h2
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-72696
Type: osv

## Details
Grav CMS before 2.0.16 contains a symlink following vulnerability in Scheduler Job::createLockFile() that allows local attackers to overwrite arbitrary files by pre-creating symlinks at predictable lock file paths in the world-writable temp directory. Attackers can place a symlink at the predictable lock path pointing to any file the web server process can write to, and the next scheduled job run will follow the symlink and overwrite the target file's content with the job ID string.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72696.json
- https://github.com/getgrav/grav/security/advisories/GHSA-q8w8-6cq5-j4h2
- https://nvd.nist.gov/vuln/detail/CVE-2026-72696
- https://www.vulncheck.com/advisories/grav-cms-before-symlink-following-via-createlockfile
