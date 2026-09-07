# [H] Grav: .htaccess file extension rules bypass via case variation on case-insensitive filesystems

## Summary
Severity: High
Advisory: GHSA-vwg3-w8w3-pc79
CVE: CVE-2026-62673
CWE: CWE-178
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-vwg3-w8w3-pc79
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.4

## Details
## Summary

The default `.htaccess` shipped with Grav (and the reference `webserver-configs/htaccess.txt`) contains security rules that block direct HTTP access to sensitive file types (`.yaml`, `.yml`, `.php`, `.json`, `.twig`, etc.) under `user/` and `system/vendor/` directories. However, these rules lack the `[NC]` (No Case) flag, making them case-sensitive. On case-insensitive filesystems (Windows/NTFS, macOS/HFS+, or Linux with Docker volumes mounted from Windows/macOS), an attacker can bypass these rules by requesting files with uppercase extensions (e.g., `.YAML`, `.PHP`, `.JSON`).

## Affected Versions

- Grav 2.0.1 (latest stable as of June 2026) — confirmed
- Grav 1.7.x — likely affected (same `.htaccess` rules)
- All versions shipping the current `webserver-configs/htaccess.txt`

## Affected Component

File: `.htaccess` (root of Grav installation)
Reference: `webserver-configs/htaccess.txt`

## Affected Rules (lines 68, 70, 72)

```apache
# Line 68 — system/vendor file types
RewriteRule ^(system|vendor)/(.*)\.(txt|xml|md|html|htm|shtml|shtm|json|yaml|yml|php|php2|php3|php4|php5|phar|phtml|pl|py|cgi|twig|sh|bat)$ error [F]

# Line 70 — user file types
RewriteRule ^(user)/(.*)\.(txt|md|json|yaml|yml|php|php2|php3|php4|php5|phar|phtml|pl|py|cgi|twig|sh|bat)$ error [F]

# Line 72 — .md files globally
RewriteRule \.md$ error [F]
```

All three rules use `[F]` without `[NC]`, making the extension match case-sensitive.

## Steps to Reproduce

1. Install Grav on a system with a case-insensitive filesystem:
   - Windows (native WAMP/XAMPP)
   - macOS (default HFS+)
   - Docker on Windows/macOS with volume mounts (e.g., `./data:/var/www/html`)

2. Create or use any plugin that stores sensitive data in its YAML config (e.g., API keys):
   ```
   user/plugins/my-plugin/my-plugin.yaml
   ```

3. Request the file with a case-varied extension:
   ```
   GET /user/plugins/my-plugin/my-plugin.YAML HTTP/1.1
   ```

4. **Expected**: HTTP 403 Forbidden
5. **Actual**: HTTP 200 OK — full file contents returned, including any API keys or sensitive configuration

## Impact

- **Information disclosure**: Plugin configuration files (`.yaml`) containing API keys, credentials, or sensitive settings can be read by unauthenticated users
- **Source code exposure**: PHP source files can be downloaded (instead of executed) when requested with `.PHP` extension on some configurations
- **Configuration exposure**: `user/config/system.yaml`, `user/config/site.yaml`, and other system configuration files are accessible

## Fix

Add the `[NC]` flag to the three affected rules:

```apache
RewriteRule ^(system|vendor)/(.*)\.(txt|xml|md|html|htm|shtml|shtm|json|yaml|yml|php|php2|php3|php4|php5|phar|phtml|pl|py|cgi|twig|sh|bat)$ error [F,NC]
RewriteRule ^(user)/(.*)\.(txt|md|json|yaml|yml|php|php2|php3|php4|php5|phar|phtml|pl|py|cgi|twig|sh|bat)$ error [F,NC]
RewriteRule \.md$ error [F,NC]
```

The `[NC]` flag makes the extension matching case-insensitive, covering `.YAML`, `.Yaml`, `.PHP`, `.Json`, etc.

## Mitigating Factors

- On native Linux with ext4 filesystem (case-sensitive), the attack does not work because Apache cannot resolve the uppercase filename to the actual file
- Grav 2.0's Twig sandbox blocks access to `plugins` config subtree from page content, preventing SSTI-based config exfiltration
- The `user/accounts/`, `user/config/`, and `user/data/` folders have separate rules (line 62, 66) that block ALL file types regardless of extension — these are not affected

## Environment

- Grav: 2.0.1
- PHP: 8.3
- Apache: 2.4 with mod_rewrite
- OS: Docker (php:8.3-apache) with volume mounted from Windows 10 (NTFS)
- Tested: June 2026

## Reporter

Sisnetic

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-vwg3-w8w3-pc79
- https://nvd.nist.gov/vuln/detail/CVE-2026-62673
- https://github.com/getgrav/grav/commit/8c9d1e7b6fd66ecea80a4bc3783fd41d36e22fb1
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav/releases/tag/2.0.4
