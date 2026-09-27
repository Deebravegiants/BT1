# [C] Piwigo RCE via PHP Code Injection into Config File in Installer

## Summary
Severity: Critical
Advisory: CVE-2026-35048
Aliases: GHSA-gphq-34pv-gvf3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-35048
Type: osv

## Details
The Piwigo installer in versions 16.3.0 and earlier accepts POST parameters for database configuration and writes them directly into a PHP configuration file without proper sanitization. On PHP 8+, the `addslashes()` protection is bypassed because it checks for `get_magic_quotes_gpc()`, a function removed in PHP 8.0. This allows raw user input to be interpolated directly into PHP source code. An unauthenticated attacker can inject arbitrary PHP code through POST parameters (prefix, dbpasswd, dbhost, dbname, or dbuser), which gets written to `local/config/database.inc.php` and executed on every page load.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35048.json
- https://github.com/Piwigo/Piwigo/security/advisories/GHSA-gphq-34pv-gvf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-35048
