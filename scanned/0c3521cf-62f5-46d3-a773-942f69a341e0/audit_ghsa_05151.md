# [M] OliveTin has Unvalidated `ot_`-prefixed Arguments that Bypass Input Filtering

## Summary
Severity: Medium
Advisory: GHSA-prj9-97mp-mwh2
CVE: CVE-2026-53541
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-24
Source: https://github.com/advisories/GHSA-prj9-97mp-mwh2
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260531214440-ebffd9f040f7

## Details
### Description

The `filterToDefinedArgumentsOnly` function in the executor is intended to discard any arguments not explicitly defined in the action's configuration. However, a special case allows any argument whose name starts with `ot_` to bypass this filter. While two system arguments (`ot_executionTrackingId` and `ot_username`) are injected by OliveTin and overridden, all other `ot_`-prefixed arguments supplied by the user pass through unmodified.

These bypassed arguments are:

1. **Not type-checked** — the validation loop only iterates over the action's defined arguments, so `ot_`-prefixed arguments skip all type safety checks entirely.
2. **Set as environment variables** — via `buildEnv()`, with completely unvalidated values, and passed to the executed command.
3. **Included in the template context** — available as `.Arguments.ot_*` in template rendering.

### Affected Code

**Filter bypass — `service/internal/executor/executor.go` (lines 728–731):**

```go
func keepArgument(name string, definedNames map[string]struct{}) bool {
    _, ok := definedNames[name]
    return ok || strings.HasPrefix(name, "ot_")
}
```

**System args only override two keys — `service/internal/executor/executor.go` (lines 742–745):**

```go
func injectSystemArgs(req *ExecutionRequest) {
    req.Arguments["ot_executionTrackingId"] = req.TrackingID
    req.Arguments["ot_username"] = req.AuthenticatedUser.Username
}
```

Any other `ot_`-prefixed argument (e.g., `ot_malicious`) survives both functions.

**Unvalidated values become environment variables — `service/internal/executor/executor.go` (lines 867–882):**

```go
func buildEnv(args map[string]string) []string {
    ret := append(os.Environ(), "OLIVETIN=1")
    for k, v := range args {
        varName := fmt.Sprintf("%v", strings.TrimSpace(strings.ToUpper(k)))
        if varName == "" { continue }
        ret = append(ret, fmt.Sprintf("%v=%v", varName, v))
    }
    return ret
}
```

The value `v` is never validated. It can contain newlines, shell metacharacters, null bytes, or any arbitrary data.

### Proof of Concept

An attacker sends a `StartAction` request with extra `ot_`-prefixed arguments:

```json
{
  "bindingId": "<any-action-id>",
  "arguments": [
    { "name": "ot_custom_var", "value": "arbitrary unvalidated content \n with newlines" },
    { "name": "ot_another",    "value": "$(whoami)" }
  ]
}
```

These arguments:

- Pass through `filterToDefinedArgumentsOnly` (the `ot_` prefix exempts them).
- Are never type-checked (not in the action's argument definitions).
- Become environment variables `OT_CUSTOM_VAR` and `OT_ANOTHER` in the executed command's environment.
- Are available in the template rendering context as `.Arguments.ot_custom_var` and `.Arguments.ot_another`.

### Impact

- **Environment variable pollution** — attacker can set arbitrary environment variables (with `OT_` uppercased prefix) in the execution environment of any action they can trigger. Scripts or programs that read custom environment variables could be influenced.
- **Potential for secondary exploitation** — if any executed script or command reads `OT_`-prefixed environment variables, the unvalidated content could cause unexpected behavior.
- **Template context pollution** — although Go's `text/template` does not recursively evaluate data values (mitigating direct template injection), the extra arguments are accessible in the template context and could interact unexpectedly with custom template logic.

### Suggested Fix

Remove the `ot_` prefix exception from `keepArgument`, or restrict it to only the two known system arguments:

```go
var systemArgs = map[string]struct{}{
    "ot_executionTrackingId": {},
    "ot_username":            {},
}

func keepArgument(name string, definedNames map[string]struct{}) bool {
    _, isDefined := definedNames[name]
    _, isSystem := systemArgs[name]
    return isDefined || isSystem
}
```

---

## Discovery Methodology

Both vulnerabilities were identified through manual source code review of the OliveTin repository, focusing on:

- Input validation boundaries (API request fields flowing into file system operations and execution contexts)
- Argument filtering and type-checking logic in the executor
- File path construction in the log persistence feature

No automated scanners or fuzzing tools were used. The review was conducted against the current `main` branch source code.

---

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-prj9-97mp-mwh2
- https://github.com/OliveTin/OliveTin/commit/ebffd9f040f791208aee1db2e5a8aecd1e3e603d
- https://github.com/OliveTin/OliveTin
