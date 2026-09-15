# [H] AVideo vulnerable to Improper Privilege Management

## Summary
Severity: High
Advisory: GHSA-2mgx-226x-8pwv
CVE: CVE-2020-23489
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2mgx-226x-8pwv
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <8.9

## Details
The import.json.php file before 8.9 for AVideo is vulnerable to a File Deletion vulnerability. This allows the deletion of configuration.php, causing certain privilege checks to not be in place, leading to privilege escalation to admin. Local File Inclusion may also leak credentials and important files.

### Patches
Upgrade to version 8.9

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-46px-7w93-j5mw
- https://nvd.nist.gov/vuln/detail/CVE-2020-23489
- https://github.com/WWBN/AVideo/issues/3117
- https://github.com/WWBN/AVideo/commit/ecc5f40470bbafff231133f58db1df70f47bfb33
- https://cube01.io/blog/Avideo-Remote-Code-Execution.html
- https://github.com/WWBN/AVideo
