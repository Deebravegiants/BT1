# [C] Adminer before 5.4.3 Remote Code Execution via SQLite VACUUM INTO

## Summary
Severity: Critical
Advisory: CVE-2026-56703
Aliases: GHSA-gmx3-g29w-77wf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-56703
Type: osv

## Details
Adminer before 5.4.3 contains a remote code execution vulnerability in SQLite query handling where VACUUM INTO is not blocked despite ATTACH restrictions. Authenticated attackers can execute VACUUM INTO to write PHP code to arbitrary file paths and execute commands on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56703.json
- https://github.com/vrana/adminer/security/advisories/GHSA-gmx3-g29w-77wf
- https://nvd.nist.gov/vuln/detail/CVE-2026-56703
- https://www.vulncheck.com/advisories/adminer-before-remote-code-execution-via-sqlite-vacuum-into
