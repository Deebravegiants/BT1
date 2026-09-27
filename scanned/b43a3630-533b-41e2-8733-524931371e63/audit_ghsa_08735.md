# [M] Nezha Monitoring: RoleMember can fire other users' cron tasks via AlertRule.FailTriggerTasks (no ownership check)

## Summary
Severity: Medium
Advisory: GHSA-rxf6-wjh4-jfj6
CVE: CVE-2026-47120
CWE: CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-23
Source: https://github.com/advisories/GHSA-rxf6-wjh4-jfj6
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=1.4.0 <1.14.15-0.20260517022419-d7526351cf97

## Details
## Summary

`createAlertRule` and `createService` (and their `update*` siblings) accept `FailTriggerTasks []uint64` and `RecoverTriggerTasks []uint64` — IDs of cron tasks to fire when the alert/service trips. The validation function only validates the alert's `Rules.Ignore` server map; it never checks that the cron task IDs in `FailTriggerTasks` / `RecoverTriggerTasks` belong to the caller.

When the alert fires, `singleton.CronShared.SendTriggerTasks(taskIDs, triggerServer)` (`service/singleton/crontask.go:113-127`) looks up those task IDs in the global cron registry and executes them via `CronTrigger`. For non-`AlertTrigger` cover modes, `CronTrigger` fans the command out to every server in `ServerShared.Range` with no ownership check.

Net effect: a `RoleMember` can attach their alert rule (or service monitor) to **another user's** cron task ID — including admin's crons. When the alert trips, the admin's cron command runs across every server (or every server in its allow/deny list).

This is the same fanout/auth-bypass class as `NEZHA-002` (cron creation), but reachable by a different code path: even if `/cron` writes are restricted to admin, this `/alert-rule` and `/service` writes are member-reachable and let a member invoke pre-existing admin crons.

## Affected versions

Commit `50dc8e660326b9f22990898142c58b7a5312b42a` and earlier on `master`.

## Reachability chain

1. `POST /api/v1/alert-rule` (or `POST /api/v1/service`) is `commonHandler`-gated — any authenticated user.
2. `createAlertRule` / `createService` accepts `FailTriggerTasks` and `RecoverTriggerTasks` from the request body without validating ownership.
3. `validateRule` (`cmd/dashboard/controller/alertrule.go:169-196`) only checks `rule.Ignore` server IDs — not the trigger task IDs.
4. `validateServers` (`cmd/dashboard/controller/service.go:543-549`) only checks the service's `SkipServers` map — not the trigger task IDs.
5. When the alert/service trips: `service/singleton/alertsentinel.go:170, 180` and `service/singleton/servicesentinel.go:747, 750` call `CronShared.SendTriggerTasks(...)`.
6. `SendTriggerTasks` (`service/singleton/crontask.go:113-127`) iterates the requested task IDs against `c.list` and calls `CronTrigger(c, triggerServer)()` for each — no ownership check.
7. `CronTrigger` then fans the cron's `Command` to every connected agent (per `Cover` rules).

## Code locations

```go
// cmd/dashboard/controller/alertrule.go:47-77
func createAlertRule(c *gin.Context) (uint64, error) {
    var arf model.AlertRuleForm
    var r model.AlertRule
    if err := c.ShouldBindJSON(&arf); err != nil { return 0, err }
    uid := getUid(c)
    r.UserID = uid
    r.Name = arf.Name
    r.Rules = arf.Rules
    r.FailTriggerTasks = arf.FailTriggerTasks       // <-- attacker-controlled task IDs
    r.RecoverTriggerTasks = arf.RecoverTriggerTasks // <-- ditto
    r.NotificationGroupID = arf.NotificationGroupID
    enable := arf.Enable
    r.TriggerMode = arf.TriggerMode
    r.Enable = &enable

    if err := validateRule(c, &r); err != nil { return 0, err }   // only checks rule.Ignore servers
    ...
}
```

```go
// cmd/dashboard/controller/alertrule.go:169-196
func validateRule(c *gin.Context, r *model.AlertRule) error {
    if len(r.Rules) > 0 {
        for _, rule := range r.Rules {
            if !singleton.ServerShared.CheckPermission(c, maps.Keys(rule.Ignore)) {
                return singleton.Localizer.ErrorT("permission denied")
            }
            // ... duration/cycle validation only
        }
    }
    // BUG: no check on r.FailTriggerTasks or r.RecoverTriggerTasks ownership.
    return nil
}
```

```go
// service/singleton/crontask.go:113-127
func (c *CronClass) SendTriggerTasks(taskIDs []uint64, triggerServer uint64) {
    c.listMu.RLock()
    var cronLists []*model.Cron
    for _, taskID := range taskIDs {
        if c, ok := c.list[taskID]; ok {                 // <-- looks up ANY cron in global state
            cronLists = append(cronLists, c)
        }
    }
    c.listMu.RUnlock()
    // BUG: no ownership check between alert.UserID and cron.UserID before invoking.
    for _, c := range cronLists {
        go CronTrigger(c, triggerServer)()
    }
}
```

```go
// service/singleton/crontask.go:138-181 — CronTrigger
return func() {
    if cr.Cover == model.CronCoverAlertTrigger {
        // alert-only: only sends to triggerServer (the member's server, when alert was triggered by it)
        if s, ok := ServerShared.Get(triggerServer[0]); ok && s.TaskStream != nil {
            s.TaskStream.Send(&pb.Task{Id: cr.ID, Data: cr.Command, Type: model.TaskTypeCommand})
        }
        return
    }
    // For Cover=CronCoverAll or CronCoverIgnoreAll: fan out to every server.
    for _, s := range ServerShared.Range {
        if cr.Cover == model.CronCoverAll && crIgnoreMap[s.ID] { continue }
        if cr.Cover == model.CronCoverIgnoreAll && !crIgnoreMap[s.ID] { continue }
        if s.TaskStream != nil {
            s.TaskStream.Send(&pb.Task{Id: cr.ID, Data: cr.Command, Type: model.TaskTypeCommand})
        }
    }
}
```

## PoC

Pre-conditions: attacker has `RoleMember` credentials. Admin has at least one pre-existing cron with `Cover=CronCoverAll` or `Cover=CronCoverIgnoreAll` (i.e., a "run on all servers" maintenance cron — common in monitoring deployments).

Step 1: Enumerate admin cron IDs by ID-guessing. Try IDs 1..N; create AlertRule referencing each, see if the alert handler accepts.

Step 2: Create an alert rule referencing the admin's cron and pointed at an offline-trigger condition on the member's own server.

```bash
TOKEN=$(curl -sX POST -H 'Content-Type: application/json' \
    -d '{"username":"member","password":"hunter2"}' \
    http://nezha.example.com/api/v1/login | jq -r .token)

curl -sX POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d '{"name":"trip","rules":[{"type":"offline","duration":3,"min":1.0,"cover":"member-server-id"}],"fail_trigger_tasks":[1,2,3,4,5],"recover_trigger_tasks":[],"notification_group_id":0,"trigger_mode":0,"enable":true}' \
    http://nezha.example.com/api/v1/alert-rule
```

Step 3: Stop the agent on the member's own server (or unplug it). The alert trips after `duration` seconds. `SendTriggerTasks([1,2,3,4,5], member-server-id)` runs.

Step 4: For each cron ID in the list, if that cron exists in the global registry and has `Cover=CronCoverAll/IgnoreAll`, its `Command` runs on every server.

The same chain works via `POST /api/v1/service` (service-monitor with `fail_trigger_tasks`).

## Composability with NEZHA-002

If `NEZHA-002` is unfixed, this chain is redundant — the member already has direct cron-create access. With `NEZHA-002` fixed, this still gives the member a means to invoke any **pre-existing** admin cron with the member's chosen trigger condition. The fix surface is also independent (alertrule/service write paths, not /cron writes).

## Suggested fix

In `validateRule` (and `validateServers`):

```go
if !singleton.CronShared.CheckPermission(c, slices.Values(r.FailTriggerTasks)) {
    return singleton.Localizer.ErrorT("permission denied")
}
if !singleton.CronShared.CheckPermission(c, slices.Values(r.RecoverTriggerTasks)) {
    return singleton.Localizer.ErrorT("permission denied")
}
```

Defense-in-depth in `SendTriggerTasks`: enforce that `task.UserID == alert.UserID || alertOwnerIsAdmin || taskOwnerIsAdmin`.

## Severity

  - PR:L because RoleMember credentials needed.
  - AC:H because attacker has to ID-guess admin cron IDs and have an alert-trip vector. (For a deployment where the attacker has visibility into max cron ID via UI hints or the `id`-query echo, AC drops to L.)
  - S:C because the cron command runs on every connected agent (different trust zone).
- **Auth:** authenticated `RoleMember`.

## Reproduction environment

- Tested against: `nezhahq/nezha` master @ `50dc8e660326b9f22990898142c58b7a5312b42a`.
- Code locations:
  - `cmd/dashboard/controller/alertrule.go:47-77` (createAlertRule), 91-131 (updateAlertRule), 169-196 (validateRule)
  - `cmd/dashboard/controller/service.go:404-445` (createService), 459-509 (updateService), 543-549 (validateServers)
  - `service/singleton/crontask.go:113-127` (SendTriggerTasks), 133-181 (CronTrigger)
  - `service/singleton/alertsentinel.go:170, 180` (alert-fire callsite)
  - `service/singleton/servicesentinel.go:742-750` (service-fire callsite)

## Reporter

Eddie Ran. Filed via reporter API. Companion to NEZHA-001/002 — same auth-bypass class but a different write path.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-rxf6-wjh4-jfj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-47120
- https://github.com/nezhahq/nezha
