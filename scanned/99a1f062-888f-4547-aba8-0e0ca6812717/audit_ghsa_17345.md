# [C] MineAdmin has an insecure default password

## Summary
Severity: Critical
Advisory: GHSA-x6mh-4w8x-p34v
CVE: CVE-2025-65854
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-x6mh-4w8x-p34v
Type: github-advisory

## Affected
- Packagist: `mineadmin/mineadmin` — affected >=0

## Details
Insecure permissions in the scheduled tasks feature of MineAdmin v3.x allows attackers to execute arbitrary commands and execute a full account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65854
- https://gist.github.com/SourByte05/1a6c6b08ac47c5d58eb7dd4422cc23b7
- https://github.com/mineadmin/mine-core/blob/7994da7f5cd0778eb9aadd550c50c259cc1d1048/src/Command/InstallProjectCommand.php#L123
- https://github.com/mineadmin/mineadmin
- http://mineadmin.com
