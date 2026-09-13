# [M] WWBN AVideo has an Unauthenticated Information Disclosure via git.json.php Exposes Developer Emails and Deployed Version

## Summary
Severity: Medium
Advisory: GHSA-52hf-63q4-r926
CVE: CVE-2026-40908
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-52hf-63q4-r926
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The file `git.json.php` at the web root executes `git log -1` and returns the full output as JSON to any unauthenticated user. This exposes the exact deployed commit hash (enabling version fingerprinting against known CVEs), developer names and email addresses (PII), and commit messages which may contain references to internal systems or security fixes.

## Details

`git.json.php` is a standalone PHP script with no authentication, no session validation, and no framework bootstrap. It directly executes a shell command and returns the result:

```php
// git.json.php — complete file
<?php
header('Content-Type: application/json');
$cmd = "git log -1";
exec($cmd . "  2>&1", $output, $return_val);

$obj = new stdClass();
$obj->output = $output;

foreach ($output as $value) {
    preg_match("/Date:(.*)/i", $value, $match);
    if (!empty($match[1])) {
        $obj->date = strtotime($match[1]);
        $obj->dateString = trim($match[1]);
        $obj->dateMySQL = date("Y-m-d H:i:s", $obj->date);
    }
}

echo json_encode($obj);
```

The file does not `require` any configuration or authentication module. It is not protected by `.htaccess` rules. The endpoint is directly accessible to any network client.

The exposed data enables:
1. **Version fingerprinting**: The commit hash identifies the exact deployed version, allowing attackers to cross-reference the project's public git history against known CVEs (AVideo has 22 published GHSAs) to determine which vulnerabilities remain unpatched on a given instance.
2. **Developer PII leakage**: Author name and email from the git commit are exposed. On self-hosted instances, this may reveal internal/corporate email addresses not otherwise publicly available.
3. **Commit message intelligence**: Commit messages may reference internal bug trackers, security fixes in progress, or infrastructure details.

## PoC

```bash
# Single unauthenticated request — no cookies, no headers needed
curl -s https://target.example/git.json.php | python3 -m json.tool
```

Verified response from test instance:
```json
{
    "output": [
        "commit 80a8af96e861cff45cd80fdd2478d00b2c07749e",
        "Author: Daniel Neto <me@danielneto.com>",
        "Date:   Wed Apr 8 16:07:23 2026 -0300",
        "",
        "    fix: Update payment response handling to include transaction token and URL"
    ],
    "date": 1775675243,
    "dateString": "Wed Apr 8 16:07:23 2026 -0300",
    "dateMySQL": "2026-04-08 19:07:23"
}
```

## Impact

- Any unauthenticated remote attacker can determine the exact deployed version and identify which known CVEs (22 published GHSAs for AVideo) apply to the target instance.
- Developer email addresses are leaked, enabling targeted phishing or social engineering against project maintainers and contributors.
- Commit messages may disclose internal project details, security fix status, or infrastructure information.

## Recommended Fix

Delete `git.json.php` entirely — it serves no user-facing purpose and exists only as a development/debug artifact:

```bash
rm git.json.php
```

If version display is needed for administrators, gate it behind authentication:

```php
<?php
require_once 'videos/configuration.php';
if (!User::isAdmin()) {
    header('HTTP/1.1 403 Forbidden');
    die(json_encode(['error' => 'Forbidden']));
}
header('Content-Type: application/json');
$cmd = "git log -1";
exec($cmd . "  2>&1", $output, $return_val);

$obj = new stdClass();
$obj->output = $output;

foreach ($output as $value) {
    preg_match("/Date:(.*)/i", $value, $match);
    if (!empty($match[1])) {
        $obj->date = strtotime($match[1]);
        $obj->dateString = trim($match[1]);
        $obj->dateMySQL = date("Y-m-d H:i:s", $obj->date);
    }
}

echo json_encode($obj);
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-52hf-63q4-r926
- https://nvd.nist.gov/vuln/detail/CVE-2026-40908
- https://github.com/WWBN/AVideo
