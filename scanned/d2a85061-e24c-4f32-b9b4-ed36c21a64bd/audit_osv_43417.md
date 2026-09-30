# [C] emlog allows unauthenticated reinstallation via `install.php?action=reinstall`.

## Summary
Severity: Critical
Advisory: CVE-2026-73849
Aliases: GHSA-v5qq-p8mp-3gxm
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-73849
Type: osv

## Details
Emlog is an open source website building system. In 2.6.26 and earlier, install.php accepts action=reinstall without authentication and deliberately skips the already-installed check because the guard runs only when $act != 'reinstall'. A remote attacker can submit hostname, dbuser, dbpasswd, dbname, dbprefix, username, password, and email values to cause file_put_contents('config.php', $config) to overwrite the configuration with attacker-controlled database settings and create a new administrator account. No fixed version is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73849.json
- https://github.com/emlog/emlog/security/advisories/GHSA-v5qq-p8mp-3gxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-73849
