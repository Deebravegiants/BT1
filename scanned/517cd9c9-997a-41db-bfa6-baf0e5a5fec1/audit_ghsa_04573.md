# [M] FUXA's scheduler API missing admin check enables operator-to-admin escalation via scheduled device actions

## Summary
Severity: Medium
Advisory: GHSA-8ghr-w65f-j3qr
CVE: CVE-2026-47721
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-8ghr-w65f-j3qr
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0

## Details
## Summary

An authorization issue in the Scheduler API allowed authenticated non-admin users to create or modify scheduled actions that should be restricted to administrators.

## Details

The Scheduler API did not correctly enforce administrator permissions when processing scheduler modifications.

As a result, authenticated users with non-administrative roles could create or modify scheduled actions that execute privileged operations, including device value changes and server-side script execution.

The issue was fixed in version 1.3.2 by enforcing the appropriate permission checks for scheduler modifications.


## Impact

An operator-level user in FUXA reaches the PLC-write and server-side-script-execution surface that the platform otherwise restricts to administrators. In a SCADA deployment those two privileges cover setpoint control and the automation scripting engine. Alice schedules a job that rewrites a pump's enable tag, opens a safety interlock, or runs a project script that walks the device tree. The scheduled-action model extends the attack: Alice does not need to keep a session open for the action to fire, and a repeating schedule re-applies her changes every cycle even if an admin reverts them manually.

**CVSS 3.1**: `AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L` (Medium, 6.3). CWE-862.

## Recommended Fix

Add `authJwt.haveAdminPermission(permission)` to both `POST /api/scheduler` and `DELETE /api/scheduler`, matching every other write endpoint that reaches `runtime.devices.setTagValue` or `runtime.scriptsMgr.runScript`.

```javascript
schedulerApp.post("/api/scheduler", secureFnc, function(req, res) {
    if (res.statusCode === 403) {
        runtime.logger.error("api post scheduler: Tocken Expired");
        return;
    }
    const permission = checkGroupsFnc(req);
    const isGuest = authJwt.isGuestUser(req.userId, req.userGroups);
    if (runtime.settings?.secureEnabled && (isGuest || !authJwt.haveAdminPermission(permission))) {
        res.status(401).json({error:"unauthorized_error", message: "Unauthorized!"});
        runtime.logger.error("api post scheduler: admin permission required");
        return;
    }
    // ... rest unchanged ...
});
```

Apply the same change to the delete handler at `server/api/scheduler/index.js:102-112`. As defense in depth, the scheduler service should also validate each `deviceActions` entry against the creator's stored groups before execution (e.g., reject `onRunScript` on any scheduler whose author is not an admin at execution time).

---
A fix is available at https://github.com/frangoteam/FUXA/releases/tag/v1.3.2.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-8ghr-w65f-j3qr
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.2
