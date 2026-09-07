# [M] OliveTin: StartActionAndWait Endpoints Bypass `logs` Permission and Return Action Output

## Summary
Severity: Medium
Advisory: GHSA-jm28-2wcr-qf3h
CVE: CVE-2026-67439
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-jm28-2wcr-qf3h
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260708085316-e421780c9885

## Details
## Summary

The synchronous execution RPCs `StartActionAndWait` and `StartActionByGetAndWait` return the full `LogEntry` for the just-executed action without checking whether the caller is allowed to read that action's logs.

OliveTin's ACL model separates `exec` from `logs`. A deployment can intentionally allow a user to run an action while denying access to its historical or live output. That separation is enforced in `GetLogs`, `GetActionLogs`, `ExecutionStatus`, and `EventStream`, but it is not enforced in the synchronous `...AndWait` endpoints.

As a result, any user who can execute an action through these endpoints can read the action output immediately even when the action's ACL explicitly sets `logs:false`.

## Details

OliveTin defines separate per-action permissions:

```go
// service/internal/config/config.go
type PermissionsList struct {
    View bool `koanf:"view"`
    Exec bool `koanf:"exec"`
    Logs bool `koanf:"logs"`
    Kill bool `koanf:"kill"`
}
```

The normal log and streaming paths correctly enforce `logs` permission:

```go
// service/internal/api/api.go
func (api *oliveTinAPI) isLogEntryAllowed(e *executor.InternalLogEntry, user *authpublic.AuthenticatedUser) bool {
    if user == nil || !isValidLogEntry(e) {
        return false
    }
    return acl.IsAllowedLogs(api.cfg, user, e.Binding.Action)
}
```

That check is used by:

- `GetLogs`
- `GetActionLogs`
- `ExecutionStatus`
- `EventStream`

However, the synchronous execution endpoints directly return the created `LogEntry` without any `logs` ACL check:

```go
// service/internal/api/api.go
func (api *oliveTinAPI) StartActionAndWait(ctx ctx.Context, req *connect.Request[apiv1.StartActionAndWaitRequest]) (*connect.Response[apiv1.StartActionAndWaitResponse], error) {
    ...
    internalLogEntry, ok := api.startActionAndWaitRun(binding, args, user)
    if !ok {
        return nil, connect.NewError(connect.CodeNotFound, fmt.Errorf("execution not found"))
    }
    return connect.NewResponse(&apiv1.StartActionAndWaitResponse{
        LogEntry: api.internalLogEntryToPb(internalLogEntry, user),
    }), nil
}

func (api *oliveTinAPI) StartActionByGetAndWait(ctx ctx.Context, req *connect.Request[apiv1.StartActionByGetAndWaitRequest]) (*connect.Response[apiv1.StartActionByGetAndWaitResponse], error) {
    ...
    internalLogEntry, ok := api.executor.GetLog(execReq.TrackingID)
    if ok {
        return connect.NewResponse(&apiv1.StartActionByGetAndWaitResponse{
            LogEntry: api.internalLogEntryToPb(internalLogEntry, user),
        }), nil
    }
    return nil, connect.NewError(connect.CodeNotFound, fmt.Errorf("execution not found"))
}
```

And `internalLogEntryToPb()` includes the full output:

```go
// service/internal/api/api.go
func (api *oliveTinAPI) internalLogEntryToPb(logEntry *executor.InternalLogEntry, authenticatedUser *authpublic.AuthenticatedUser) *apiv1.LogEntry {
    pble := &apiv1.LogEntry{
        ActionTitle:         logEntry.ActionTitle,
        Output:              logEntry.Output,
        ExitCode:            logEntry.ExitCode,
        ExecutionTrackingId: logEntry.ExecutionTrackingID,
        ...
    }
    ...
    return pble
}
```

The executor separately enforces `exec` permission, but there is no subsequent check that the response should omit or deny `Output` when `logs:false`.

## Local Reproduction

I verified this locally with a one-off test against the real `StartActionAndWait` handler.

Configuration used:

- action `secret_action` with shell `echo SECRET_FROM_ACTION`
- user `low` matched by ACL:
  - `exec: true`
  - `logs: false`
  - `view: false`
  - `kill: false`

Then I invoked `StartActionAndWait` as `low` through the real handler path using header-based auth.

Observed output from the test run:

```text
=== RUN   TestTempStartActionAndWaitLeaksOutputWithoutLogsPermission
time="2026-03-12T23:36:33+01:00" level=info msg="Action requested" actionTitle=secret-action tags="[]"
time="2026-03-12T23:36:33+01:00" level=info msg="Action parse args - Before" actionTitle=secret-action cmd="echo SECRET_FROM_ACTION"
time="2026-03-12T23:36:33+01:00" level=info msg="Action parse args - After" actionTitle=secret-action cmd="echo SECRET_FROM_ACTION"
time="2026-03-12T23:36:33+01:00" level=info msg="Action started" actionTitle=secret-action timeout=5
time="2026-03-12T23:36:33+01:00" level=info msg="Action finished" actionTitle=secret-action exit=0 outputLength=40 timedOut=false
    temp_acl_bypass_test.go:56: output="S\x00E\x00C\x00R\x00E\x00T\x00_\x00F\x00R\x00O\x00M\x00_\x00A\x00C\x00T\x00I\x00O\x00N\x00\r\x00\n\x00" blocked=false action="secret-action"
--- PASS: TestTempStartActionAndWaitLeaksOutputWithoutLogsPermission (0.03s)
```

The UTF-16LE formatting is from Windows `echo`, but the key result is that the response returned the real command output even though the caller's ACL explicitly denied log access.

## Impact

- **Bypass of log confidentiality controls:** Operators may configure actions to be executable but not log-readable. The `...AndWait` endpoints break that separation.
- **Disclosure of secrets printed by actions:** Many OliveTin actions wrap administrative scripts and commands whose stdout/stderr may contain credentials, internal paths, hostnames, tokens, or sensitive operational data.
- **Adjacent to previous output-leak bugs:** OliveTin already had an EventStream output disclosure bug. This is a separate response-path authorization gap on the synchronous execution APIs.

## Recommended Fix

Enforce `logs` permission before returning `LogEntry` content from synchronous execution endpoints.

Two reasonable fixes:

1. Deny the endpoint response when `logs:false`

```go
if !acl.IsAllowedLogs(api.cfg, user, binding.Action) {
    return nil, connect.NewError(connect.CodePermissionDenied, fmt.Errorf("permission denied to view action output"))
}
```

2. Or redact log-bearing fields when `logs:false`

```go
pb := api.internalLogEntryToPb(internalLogEntry, user)
if !acl.IsAllowedLogs(api.cfg, user, binding.Action) {
    pb.Output = ""
    pb.ExitCode = 0
}
return connect.NewResponse(&apiv1.StartActionAndWaitResponse{LogEntry: pb}), nil
```

The same fix should be applied to both:

- `StartActionAndWait`
- `StartActionByGetAndWait`

## References

- `service/internal/api/api.go`
- `service/internal/config/config.go`
- `service/internal/acl/acl.go`

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-jm28-2wcr-qf3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-67439
- https://github.com/OliveTin/OliveTin/commit/e421780c9885aa5024d2f47b4ed4898f2f18eb90
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.17.0
