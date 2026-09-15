# [M] CVE-2026-40016

## Summary
Severity: Medium
Advisory: CVE-2026-40016
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-40016
Type: osv

## Details
Attacker can upload a malicious Sieve script over ManageSieve service (or locally) to bypass configured CPU time limits for Sieve up to 130 times of the configured limit. Attacker can use this to degrade server performance and bypass configured CPU time limits for Sieve scripts. Install fixed version, or alternatively prevent direct access to Sieve scripts via ManageSieve or local access. No publicly available exploits are known.

## References
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0002.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40016.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40016
