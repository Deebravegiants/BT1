# [C] baserCMS has OS Command Injection Leading to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: GHSA-qxmc-6f24-g86g
CVE: CVE-2026-21861
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-qxmc-6f24-g86g
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <5.2.3

## Details
## Summary

In the core update functionality of baserCMS, some parameters sent from the admin panel are passed to the `exec()` function without proper validation or escaping. This issue allows **an authenticated CMS administrator to execute arbitrary OS commands on the server (Remote Code Execution, RCE)**.

This vulnerability is not a UI-level issue such as screen manipulation or lack of CSRF protection, but rather stems from **a design that directly executes input values received on the server side as OS commands**. Therefore, even if buttons are hidden in the UI, or even if CakePHP's CSRF/FormProtection (SecurityComponent) ensures that only legitimate POST requests are accepted, **an attack is possible as long as a request containing a valid token is processed within an administrator session**.

---

## Vulnerability Information

| Item | Details |
| ---- | ------- |
| CWE | CWE-78: Improper Neutralization of Special Elements used in an OS Command |
| Impact | Remote Code Execution (RCE) |
| Severity | Critical |
| Attack Requirements | Administrator privileges required |
| Reproducibility | Reproducible (confirmed multiple times) |
| Test Environment | baserCMS 5.2.2 (Docker / development environment) |

---

## Affected Areas

- **Controller**
  - `PluginsController::get_core_update()`
- **Service**
  - `PluginsService::getCoreUpdate()`
- **Affected Endpoint**
  - `/baser/admin/baser-core/plugins/get_core_update`

---

## Technical Details

### Vulnerable Code Flow

```text
PluginsController::get_core_update()
  ↓ Retrieves php parameter from POST data
PluginsService::getCoreUpdate($targetVersion, $php, $force)
  ↓ Concatenates $php into command string without validation or escaping
exec($command)
```

### Relevant Code (Excerpt)

**PluginsController.php**

```php
$service->getCoreUpdate(
    $request->getData('targetVersion') ?? '',
    $request->getData('php') ?? 'php',
    $request->getData('force'),
);
```

**PluginsService.php**

```php
$command = $php . ' ' . ROOT . DS . 'bin' . DS . 'cake.php composer ' .
           $targetVersion . ' --php ' . $php . ' --dir ' . TMP . 'update';

exec($command, $out, $code);
```

The `$php` parameter is user input, and **none** of the following countermeasures are in place:

- Restriction via allowlist
- Validation via regular expression
- Escaping via `escapeshellarg()` or similar

---

## Attack Scenario

1. The attacker logs in as a CMS administrator
2. Sends a POST request to the core update functionality in the admin panel
3. Specifies a string containing OS commands in the `php` parameter
4. `exec()` is executed on the server side, running the arbitrary OS command

### Example Attack Input (Conceptual)

```text
php=php;id>/tmp/rce_test;#
```

---

## Verification Results (PoC)

### Execution Result

```bash
$ docker exec bc-php cat /tmp/rce_test
uid=1000(www-data) gid=1000(www-data) groups=1000(www-data)
```

The above confirms that OS commands can be executed with `www-data` privileges.

### Additional Notes

- Reproducible through the legitimate flow in the admin panel (browser)
- Succeeds even with CSRF/FormProtection tokens included in a legitimate request
- Failure cases (400/403) have also been investigated and differentiated
- Confirmed reproducible via resending HTTP requests with tools such as curl (resending the same request containing valid tokens)

---

## Impact

If this vulnerability is exploited, the following becomes possible:

- Retrieval of server information
- Reading/writing arbitrary files
- Retrieval of application configuration information (DB credentials, etc.)
- OS-level operations beyond application permission boundaries

Although administrator privileges are required, **this is a design issue where the impact extends from the application layer to the OS layer**, and the impact is considered significant.

---

## Recommended Fix

### Primary Recommendation

- Do not accept the PHP executable path from user input
- Fix the PHP executable on the server side using the `PHP_BINARY` constant

```php
$php = escapeshellarg(PHP_BINARY);
```

### Supplementary Fix Recommendations

- Apply `escapeshellarg()` escaping to other command-line arguments (version number, directory, etc.) as well
- If possible, consider using execution methods that do not involve shell interpretation (array format, Process class, etc.)

### Alternative (Not Recommended)

- Allowlist validation for the PHP executable path
- Combined use of regex validation and `escapeshellarg()`

However, **from the perspective of reducing the attack surface, a design that eliminates user input entirely is recommended**.

---

## Additional Notes

- This issue is independent of UI display controls (showing/hiding buttons)
- As long as the endpoint exists, an attack is possible if a request containing valid tokens is processed
- This is a problem stemming from the design-level handling of input, and cannot be prevented by CSRF or UI controls alone

---

## Conclusion

Due to a design issue in baserCMS's core update functionality where user input is passed to `exec()` without validation, **Remote Code Execution (RCE) is achievable with administrator privileges**. This vulnerability can be fixed through input validation and design review, and prompt remediation is recommended.

This advisory was translated from Japanese to English using GitHub Copilot.

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-qxmc-6f24-g86g
- https://nvd.nist.gov/vuln/detail/CVE-2026-21861
- https://basercms.net/security/JVN_20837860
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/5.2.3
