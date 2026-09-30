# [M] AVideo's WebSocket Token Never Expires Due to Commented-Out Timeout Validation in verifyTokenSocket()

## Summary
Severity: Medium
Advisory: GHSA-2mg4-pfgx-64cf
CVE: CVE-2026-34362
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-2mg4-pfgx-64cf
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `verifyTokenSocket()` function in `plugin/YPTSocket/functions.php` has its token timeout validation commented out, causing WebSocket tokens to never expire despite being generated with a 12-hour timeout. This allows captured or legitimately obtained tokens to provide permanent WebSocket access, even after user accounts are deleted, banned, or demoted from admin. Admin tokens grant access to real-time connection data for all online users including IP addresses, browser info, and page locations.

## Details

WebSocket tokens are generated via `getEncryptedInfo()` which calls `getToken(43200)` to create a token with a 12-hour expiration window. The token is encrypted and contains security-critical claims: `isAdmin`, `from_users_id`, `user_name`, IP, browser, and device ID.

The regular HTTP token verification at `objects/functions.php:3437-3439` enforces the timeout:

```php
// objects/functions.php:3437-3439
if (!($time >= $obj->time && $time <= $obj->timeout)) {
    _error_log("verifyToken token timout...");
    return false;  // <-- enforced
}
```

But the WebSocket-specific verification at `plugin/YPTSocket/functions.php:65-82` has the enforcement commented out:

```php
// plugin/YPTSocket/functions.php:77-80
if (!($time >= $obj->time && $time <= $obj->timeout)) {
    //_error_log("verifyToken token timout...");
    //return false;  // <-- NOT enforced, always falls through to return true
}
return true;
```

**Execution flow:**

1. Client connects to WebSocket with `?webSocketToken=TOKEN` in URL query
2. `onOpen()` (Message.php:34) calls `getDecryptedInfo($wsocketGetVars['webSocketToken'])` (line 48)
3. `getDecryptedInfo()` (functions.php:49) decrypts the token and calls `verifyTokenSocket($json->token)` (line 54)
4. `verifyTokenSocket()` validates the salt (passes) but the timeout check at line 77 evaluates the condition without acting on failure — `return false` is commented out
5. Function returns `true` — connection established with all token claims (`isAdmin`, `from_users_id`) trusted

**Impact amplification via isAdmin:**

When a connection has `isAdmin=true` (from token, Message.php:58), the `getTotals()` function (Message.php:419-432) includes detailed data about every connected client in periodic broadcast messages:

```php
// Message.php:419-432
if ($isAdmin) {
    $index = md5($client['selfURI']);
    // Exposes: selfURI, yptDeviceId, users_id, user_name, browser, ip, location
    $return['users_uri'][$index][$client['yptDeviceId']][$client['users_id']] = $client;
}
```

Additionally, the `webSocketToken` message type (Message.php:212-217) allows anonymous connections (`users_id=0`) to upgrade their identity by providing a captured token, meaning stolen tokens work from new connections indefinitely.

The 10-minute inactivity timeout (Message.php:135-143) is not a mitigation — it only closes idle connections and resets on every message (line 243).

## PoC

```bash
# Step 1: Obtain a WebSocket token as any authenticated user
curl -s -b 'PHPSESSID=VALID_SESSION' \
  'https://target.com/plugin/YPTSocket/getWebSocket.json.php' | jq -r '.webSocketToken'
# Save as TOKEN=<output>

# Step 2: Wait for the token to expire (>12 hours)
# In a real scenario, the attacker already has a previously captured token

# Step 3: Connect with the expired token — succeeds because verifyTokenSocket() skips timeout
wscat -c 'ws://target.com:8888/?webSocketToken=TOKEN'

# Step 4: Verify the connection is established and receiving broadcasts
# The server will send periodic getTotals data

# Step 5: If the token was from an admin, the getTotals response includes
# all connected clients' selfURI, IP, browser, device ID, user_name, and location

# Step 6: Any user can also enumerate connected users without admin:
# Send: {"msg":"getClientsList","webSocketToken":"TOKEN"}
# Response includes all users_id, isAdmin status, and usernames
```

**Scenario: Demoted admin retains permanent admin WebSocket access**
1. Admin user obtains WebSocket token (contains `isAdmin: true`)
2. Admin is demoted to regular user via the web interface
3. Admin's WebSocket token still works indefinitely — the `isAdmin` claim in the token is never re-validated
4. Demoted user continues receiving all connected users' IPs, locations, and browsing activity

## Impact

- **Permanent access after credential revocation:** Deleted, banned, or suspended users retain WebSocket access with their original identity and privilege level, undermining account lifecycle management.
- **Privilege persistence after demotion:** Admin users who are demoted retain admin-level WebSocket access indefinitely. The `isAdmin` flag baked into the token is never re-checked against the database.
- **Real-time surveillance via admin tokens:** Admin-level tokens expose all connected users' IP addresses, geographic locations (if User_location plugin enabled), current page URLs (selfURI), browser fingerprints, and device IDs — enabling real-time tracking of user activity.
- **Extended attack window for token theft:** Any vulnerability that leaks a WebSocket token (XSS, log exposure, network interception) provides permanent rather than 12-hour access, significantly increasing the impact of token compromise.
- **Identity hijacking:** The `webSocketToken` message type allows using a stolen token to assume another user's identity on new connections, enabling impersonation in chat and messaging.

## Recommended Fix

Uncomment the timeout enforcement in `verifyTokenSocket()` at `plugin/YPTSocket/functions.php:77-80`:

```php
function verifyTokenSocket($token) {
    global $global;
    $obj = _json_decode(decryptString($token));
    if (empty($obj)) {
        _error_log("verifyToken invalid token");
        return false;
    }
    if ($obj->salt !== $global['salt']) {
        _error_log("verifyToken salt fail");
        return false;
    }
    $time = time();
    if (!($time >= $obj->time && $time <= $obj->timeout)) {
        _error_log("verifyToken token timeout time = $time; obj->time = $obj->time; obj->timeout = $obj->timeout");
        return false;  // <-- uncomment this line
    }
    return true;
}
```

Additionally, consider:
1. Adding an admin check to the `getClientsList` handler (Message.php:219) so only admins can enumerate connected users.
2. Re-validating the `isAdmin` claim against the database periodically rather than trusting the token claim for the lifetime of the connection.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-2mg4-pfgx-64cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34362
- https://github.com/WWBN/AVideo/commit/5d5237121bf82c24e9e0fdd5bc1699f1157783c5
- https://github.com/WWBN/AVideo
