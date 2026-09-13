# [H] FrankenPHP leaks session data between requests in worker mode

## Summary
Severity: High
Advisory: GHSA-r3xh-3r3w-47gp
CVE: CVE-2026-24894
CWE: CWE-269, CWE-384, CWE-613
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-r3xh-3r3w-47gp
Type: github-advisory

## Affected
- Go: `github.com/dunglas/frankenphp` — affected >=0 <1.11.2

## Details
### Summary

When running FrankenPHP in **worker mode**, the `$_SESSION` superglobal is not correctly reset between requests. This allows a subsequent request processed by the same worker to access the `$_SESSION` data of the previous request (potentially belonging to a different user) before `session_start()` is called.

### Details

In standard PHP execution, the environment is torn down completely after every request. In FrankenPHP's worker mode, the application stays in memory, and superglobals are manually reset between requests.

The vulnerability exists because `$_SESSION` is stored in the Zend Engine's symbol table (`EG(symbol_table)`). While the standard PHP request shutdown (RSHUTDOWN) decrements the reference count of the session data, it does not remove the `$_SESSION` variable itself from the symbol table. FrankenPHP's reset logic (`frankenphp_reset_super_globals`) previously cleared other superglobals but failed to explicitly delete `$_SESSION`.

Consequently, until `session_start()` is called in the new request (which re-initializes the variable), the `$_SESSION` array retains the data from the previous request processed by that specific worker thread.

### Impact

This is a **cross-request data leakage** vulnerability.

* **Confidentiality:** If an application reads `$_SESSION` before calling `session_start()`, it can access sensitive information (authentication tokens, user IDs, PII) belonging to the previous user.
* **Logic Errors / Impersonation:** If application logic relies on `$_SESSION` being empty or unset to detect a "guest" state, or checks for specific keys in `$_SESSION` prior to session initialization, a malicious actor (or accidental race condition) could trigger privilege escalation or user impersonation.

This affects only users running FrankenPHP in **worker mode** and not `session_start()` for each request, which is done by default by most frameworks.

### PoC

The following steps demonstrate the issue (derived from the regression tests added in the fix):

1. **Client A** sends a request that starts a session and sets sensitive data:

```php
// Request 1
session_start();
$_SESSION['secret'] = 'AliceData';
session_write_close();
```

2. **Client B** (or the same client without cookies) sends a request to the same worker. This script checks `$_SESSION` *without* starting a session:

```php
// Request 2
// session_start() is NOT called
if (!empty($_SESSION)) {
    echo "Leaked Data: " . $_SESSION['secret'];
}
```


3. **Result:** Client B receives "Leaked Data: AliceData".

### Workarounds

* Ensure `session_start()` is called immediately at the entry point of your worker script to overwrite any residual data (though this may not cover all edge cases if middleware runs before the controller).
* Manually unset `$_SESSION` at the very beginning of the worker loop, before handling the request.

## References
- https://github.com/php/frankenphp/security/advisories/GHSA-r3xh-3r3w-47gp
- https://nvd.nist.gov/vuln/detail/CVE-2026-24894
- https://github.com/php/frankenphp/commit/24d6c991a7761b638190eb081deae258143e9735
- https://github.com/php/frankenphp
- https://github.com/php/frankenphp/releases/tag/v1.11.2
