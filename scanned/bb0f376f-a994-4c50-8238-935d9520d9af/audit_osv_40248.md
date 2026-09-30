# [M] Possible to hijack modules in current working directory

## Summary
Severity: Medium
Advisory: CVE-2026-5271
Aliases: GHSA-jr5x-hgm4-rrm6
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-5271
Type: osv

## Details
pymanager included the current working directory in sys.path meaning modules could be shadowed by modules in the current working directory. As a result, if a user executes a pymanager-generated command (e.g., pip, pytest)
 from an attacker-controlled directory, a malicious module in that 
directory can be imported and executed instead of the intended package.

## References
- http://www.openwall.com/lists/oss-security/2026/04/01/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5271.json
- https://github.com/python/pymanager/security/advisories/GHSA-jr5x-hgm4-rrm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-5271
- https://github.com/python/pymanager
