# [H] FUXA: Unauthenticated SSRF via Socket.IO DEVICE_WEBAPI_REQUEST and DEVICE_PROPERTY with response reading

## Summary
Severity: High
Advisory: GHSA-w86f-rf9w-h3x6
CVE: CVE-2026-47719
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-w86f-rf9w-h3x6
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0

## Details
## Summary

An unauthenticated attacker (Alice) connects to FUXA's Socket.IO endpoint and emits a `device-webapi-request` event whose `property.address` field names an arbitrary URL. FUXA's `DEVICE_WEBAPI_REQUEST` handler at `server/runtime/index.js:296` calls `axios.get(address)` server-side and broadcasts the full response body back on the same event via `io.emit`. The companion handler `DEVICE_PROPERTY` at `server/runtime/index.js:153` has the same miss against OPC UA and ODBC endpoints. Both handlers skip the `isSocketWriteAuthorized()` check that the other write-capable events (`DEVICE_VALUES` at line 182, `DEVICE_ENABLE` at line 358) call. Alice reads cloud instance metadata, scans internal services, and connects to any OPC UA server or ODBC database the FUXA host can reach, then receives the results.

## Details

**Vulnerable handlers**: `server/runtime/index.js:153-171, 296-316`:

```javascript
socket.on(Events.IoEventTypes.DEVICE_PROPERTY, (message) => {
    try {
        if (message && message.endpoint && message.type) {
            devices.getSupportedProperty(message.endpoint, message.type).then(result => {
                message.result = result;
                io.emit(Events.IoEventTypes.DEVICE_PROPERTY, message);
            })
            // ...
        }
    }
    // ...
});

socket.on(Events.IoEventTypes.DEVICE_WEBAPI_REQUEST, (message) => {
    try {
        if (message && message.property) {
            devices.getRequestResult(message.property).then(result => {
                message.result = result;
                io.emit(Events.IoEventTypes.DEVICE_WEBAPI_REQUEST, message);
            })
            // ...
        }
    }
    // ...
});
```

**Sink**: `server/runtime/devices/httprequest/index.js:471` for the webapi path:

```javascript
if (property.method === 'GET') {
    axios.get(property.address).then(res => {
        resolve(res.data);
    // ...
```

Alice fully controls `property.address`, and `io.emit` echoes the response body back on the same event. For the ODBC variant, `server/runtime/devices/odbc/index.js` builds the connection string from `endpoint.address` plus `endpoint.uid` and `endpoint.pwd`, so Alice supplies credentials and targets any reachable ODBC server.

**Contrast**: `server/runtime/index.js:182` (the DEVICE_VALUES write handler) gates the exact same kind of action behind `isSocketWriteAuthorized(socket)`. The two handlers above skip that check.

Reachability: neither handler performs any authorization check, so both modes reach the sinks. `secureEnabled=true` does not close the gap because the Socket.IO connect block at `server/runtime/index.js:114-120` auto-issues a guest token to any client that connects without one, and the handlers run regardless of `socket.isAuthenticated`. This is the same pattern GHSA-vwcg-c828-9822's note warned about: enabling authentication does not mitigate the missing check here.


## Impact

Alice uses FUXA as a read-SSRF oracle against any HTTP(S) service the FUXA host can reach, with the response body delivered back to her Socket.IO session. On cloud-hosted SCADA deployments this exfiltrates IAM credentials from the instance metadata service. On OT networks it reaches internal OPC UA servers, ODBC databases, and administrative consoles that have no other external exposure. The ODBC variant accepts attacker-supplied credentials, so Alice authenticates to any ODBC server that trusts connections from the FUXA host. The attack works against `secureEnabled=true` deployments as well as the default; no operator interaction required.

**CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N` (High, 8.2). CWE-918.

## Recommended Fix

Add the existing `isSocketWriteAuthorized(socket)` check at the top of both handlers, matching the pattern used by `DEVICE_VALUES` and `DEVICE_ENABLE`. Also switch `io.emit` to `socket.emit` so the response scopes to the requesting socket instead of broadcasting to every connected client. For defense in depth, validate `property.address` against an allowlist of schemes and reject private, loopback, and link-local address ranges before calling `axios.get` or the device connect paths.

```javascript
socket.on(Events.IoEventTypes.DEVICE_WEBAPI_REQUEST, (message) => {
    try {
        if (!isSocketWriteAuthorized(socket)) {
            logger.warn(`${Events.IoEventTypes.DEVICE_WEBAPI_REQUEST}: unauthorized request from ${socket.userId || 'guest'}`);
            return;
        }
        if (message && message.property) {
            // ... validate property.address against allowlist ...
            devices.getRequestResult(message.property).then(result => {
                message.result = result;
                socket.emit(Events.IoEventTypes.DEVICE_WEBAPI_REQUEST, message);
            })
            // ...
        }
    }
    // ...
});
```

Apply the same three changes (auth check, `socket.emit`, address validation) to `DEVICE_PROPERTY`.

---
A fix is available at https://github.com/frangoteam/FUXA/releases/tag/v1.3.2.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-w86f-rf9w-h3x6
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.2
