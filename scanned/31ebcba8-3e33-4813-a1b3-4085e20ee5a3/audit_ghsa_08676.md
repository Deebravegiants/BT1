# [H] FUXA's Unauthenticated Project Data Disclosure Exposes Server-Side Scripts and Device Configurations

## Summary
Severity: High
Advisory: GHSA-q3w6-q3hc-c5x6
CVE: CVE-2026-47717
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-q3w6-q3hc-c5x6
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=1.3.0 <1.3.1

## Details
### Summary

The GET /api/project endpoint exposes sensitive project configuration data to guest-context requests even when secureEnabled is enabled.

### Details

File: `server/api/projects/index.js`

```javascript
prjApp.get("/api/project", secureFnc, function(req, res) {
    const permission = checkGroupsFnc(req);
    runtime.project.getProject(req.userId, permission).then(result => {
        if (result) {
            res.json(result);
        }
    });
});
```

The endpoint uses the `secureFnc` middleware, but this middleware calls `verifyToken` in `server/api/jwt-helper.js` which auto-generates a valid guest JWT when no token is provided (line 49-51):

```javascript
if (!token) {
    token = getGuestToken();
}
```

The guest token is signed with the server's secret and passes verification. The handler then calls `getProject` which returns the full project data. The `_filterProjectPermission` function (line 924 of `server/runtime/project/index.js`) filters some UI elements for non-admin users, but it does not remove scripts, devices, alarms, or other sensitive configuration data.

### PoC

**Environment**

- FUXA v1.3.0-2773 (`frangoteam/fuxa:latest`)
- `secureEnabled: true` with a random `secretCode`

**Retrieve full project data without authentication:**

```bash
curl -s http://192.168.32.129:1881/api/project
```

```json
{
  "scripts": [
    {
      "id": "SCRIPT_ID",
      "name": "calculate"
    },
  ]
}
```

No authentication token, API key, or cookie was provided. The response includes:

- **Server-side scripts**: full source code, IDs, names, execution mode, and permission levels. This reveals internal automation logic and sensitive project structure information that could assist further attacks against the deployed system.
- **Device configurations**: and communication endpoint information may also be exposed depending on the deployed project configuration.
- **HMI views**: the full SVG content and layout of every operator screen, including variable bindings that map UI elements to device tags.
- **Alarm definitions**: alarm thresholds, conditions, and notification settings when configured.

### Impact

The endpoint may expose sensitive project configuration data including script metadata, device connection information, HMI configuration, and alarm definitions. In industrial environments this information can assist further targeted attacks against the deployed system.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-q3w6-q3hc-c5x6
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.1
