# [M] motionEye's missing authentication on ActionHandler allows unauthenticated camera action execution

## Summary
Severity: Medium
Advisory: GHSA-j67x-q29f-qcvv
CVE: CVE-2026-55863
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-j67x-q29f-qcvv
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.44.0

## Details
## Summary

The `ActionHandler.post()` method in motionEye has no authentication decorator, allowing any unauthenticated attacker to trigger camera actions including snapshots, recording start/stop, and configured action scripts (PTZ controls, alarm triggers, etc.).

## Vulnerability Details

**File**: `motioneye/handlers/action.py` — `ActionHandler.post()` line 36
**CWE**: CWE-862 — Missing Authorization
**CVSS**: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N = 5.3 Medium

### Vulnerable Code

```python
class ActionHandler(BaseHandler):
    async def post(self, camera_id, action):   # ← NO @BaseHandler.auth() decorator
        camera_id = int(camera_id)
        if camera_id not in config.get_camera_ids():
            raise HTTPError(404, 'no such camera')
        ...
        if action == 'snapshot':
            await self.snapshot(camera_id)   # executed without auth
            return
        elif action == 'record_start':
            return self.record_start(camera_id)
        elif action == 'record_stop':
            return self.record_stop(camera_id)

        action_commands = config.get_action_commands(local_config)
        command = action_commands.get(action)
        ...
        self.run_command_bg(command)   # executes predefined shell scripts
```

Compare with other handlers that correctly require authentication:

```python
@BaseHandler.auth(admin=True)   # ← properly protected
async def delete(self, camera_id, filename):
    ...
```

## Steps to Reproduce

1. Deploy motionEye with at least one camera configured
2. Send unauthenticated POST:

```
POST /action/1/snapshot HTTP/1.1
Host: motioneye-host:8765
Content-Length: 0
```

3. Observe `{}` (HTTP 200) response — snapshot triggered without any credentials

For action scripts (`lock`, `unlock`, `alarm_on`, `alarm_off`, `light_on`, etc.):
```
POST /action/1/alarm_on HTTP/1.1
Host: motioneye-host:8765
```

## Impact

- Unauthenticated attacker can trigger camera snapshots on demand
- Unauthenticated attacker can start/stop video recording
- If action scripts are configured by admin: attacker can trigger PTZ movement, alarm control, lighting changes — physical security bypass
- Via remote cameras: SSRF by triggering action on a remote motionEye server

## Verification

Dynamically confirmed on v0.43.1 in Docker lab — `POST /action/2/snapshot` with no credentials returns HTTP 200 `{}`. Server log shows the action was processed (failed only because motion daemon was not running for the test camera, not due to an auth rejection).

## Recommended Fix

```python
class ActionHandler(BaseHandler):
    @BaseHandler.auth()   # add authentication requirement
    async def post(self, camera_id, action):
        ...
```

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-j67x-q29f-qcvv
- https://github.com/motioneye-project/motioneye
