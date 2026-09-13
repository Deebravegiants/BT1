# [C] File Browser: Command Injection via Authentication Hook Shell Substitution (Pre-Authentication RCE)

## Summary
Severity: Critical
Advisory: GHSA-m93h-4hw7-5qcm
CVE: CVE-2026-54088
CWE: CWE-306, CWE-78, CWE-88
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-m93h-4hw7-5qcm
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.6

## Details
## Overview

The Hook Authentication feature in File Browser allows administrators to delegate login verification to an external shell command. User-supplied credentials (username and password) are interpolated into this command string using `os.Expand` without sanitization. An **unauthenticated remote attacker** can inject shell metacharacters in the username or password field at the login screen, causing the server to execute arbitrary OS commands before any authentication takes place. This is a **critical pre-authentication RCE**.

## Affected Location

- **File:** `auth/hook.go`
- **Function:** `HookAuth.RunCommand`

## CVSS v4.0

| Metric | Value | Rationale |
|---|---|---|
| Attack Vector (AV) | Network (N) | Exploitable via the login endpoint over HTTP from any network |
| Attack Complexity (AC) | Low (L) | Single crafted HTTP request; no preparation needed |
| Attack Requirements (AT) | None (N) | No race condition or special timing required |
| Privileges Required (PR) | **None (N)** | **No account required — pre-authentication attack** |
| User Interaction (UI) | None (N) | Fully automated; no victim action needed |
| Vulnerable System Confidentiality (VC) | High (H) | Full read access to server filesystem and env |
| Vulnerable System Integrity (VI) | High (H) | Arbitrary file write/modification |
| Vulnerable System Availability (VA) | High (H) | Can kill processes, exhaust resources |
| Subsequent System Confidentiality (SC) | None (N) | No direct impact on downstream systems assumed |
| Subsequent System Integrity (SI) | None (N) | — |
| Subsequent System Availability (SA) | None (N) | — |

**Vector String:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
**Base Score: 9.3 (Critical)**

> **Note:** `PR:None` is the critical differentiator from vulnerabilities 01 and 02. Because the injection point is the unauthenticated login endpoint, no account or session is required. A single HTTP request to the login API is sufficient to achieve RCE.

## CWE

| ID | Name | Role |
|---|---|---|
| [CWE-78](https://cwe.mitre.org/data/definitions/78.html) | Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') | Primary — attacker-supplied credentials embedded in shell command string via `os.Expand` |
| [CWE-88](https://cwe.mitre.org/data/definitions/88.html) | Improper Neutralization of Argument Delimiters in a Command ('Argument Injection') | Secondary — `$USERNAME`/`$PASSWORD` expansion injects additional shell commands |
| [CWE-306](https://cwe.mitre.org/data/definitions/306.html) | Missing Authentication for Critical Function | Secondary — OS command execution is reachable before any authentication is verified |

## Technical Details

`HookAuth.RunCommand` builds the authentication command and substitutes credential values using `os.Expand`:

```go
// auth/hook.go
envMapping := func(key string) string {
    switch key {
    case "USERNAME":
        return a.Cred.Username  // directly from the HTTP login request body
    case "PASSWORD":
        return a.Cred.Password  // directly from the HTTP login request body
    default:
        return os.Getenv(key)
    }
}

for i, arg := range command {
    if i == 0 { continue }
    command[i] = os.Expand(arg, envMapping) // no escaping applied
}
```

`os.Expand` performs plain text substitution. There is no escaping, quoting, or validation of the credential values before they are embedded into the command string.

If an admin has configured the hook authentication command as:

```
sh -c "test $USERNAME = 'admin'"
```

...and an attacker submits the username `; id #` at the login screen, the expanded command becomes:

```sh
sh -c "test ; id # = 'admin'"
```

The `;` terminates the `test` expression and the shell executes `id`. The `#` comments out the remainder, preventing a syntax error. The attacker's command runs with the privileges of the File Browser process — **without needing a valid account or password**.

## Attack Scenario / Reproduction Steps

1. Admin enables Hook Authentication and sets the command to:
   ```
   sh -c "test $USERNAME = 'admin'"
   ```
2. An unauthenticated attacker sends a login request (e.g., via `curl` or the web UI) with:
   - **Username:** `; id #`
   - **Password:** (any value)
3. The server executes:
   ```sh
   sh -c "test ; id # = 'admin'"
   ```
4. The `id` command runs on the server, confirming pre-authentication RCE.

No account is needed. The attacker does not need to know any valid credentials. A single request is sufficient.

## Impact

An unauthenticated remote attacker can execute arbitrary OS commands on the server under the privilege level of the File Browser process. This is the most severe class of vulnerability in this codebase:

- **No authentication required** — exposed to the entire internet if the service is public-facing.
- **Single request** — no setup, no enumeration, no prior foothold.
- Full server compromise: data exfiltration, persistent backdoor installation, lateral movement to internal networks.

Any internet-facing File Browser instance with Hook Authentication enabled is fully compromised by a single malformed login attempt.

## Proof of Concept

```go
package auth

import (
        "os"
        "strings"
        "testing"
)

func TestPoC_AuthHookInjection(t *testing.T) {
        // Simulate the admin-configured hook authentication command.
        // This represents a realistic configuration: verify the username via a shell expression.
        a := &HookAuth{
                Command: "sh -c $USERNAME",
                Cred: hookCred{
                        // Attacker-supplied username from the login form.
                        // The password is irrelevant.
                        Username: "id ; echo injected",
                        Password: "anything",
                },
        }

        // Simulate the RunCommand logic in auth/hook.go
        command := strings.Split(a.Command, " ")

        envMapping := func(key string) string {
                if key == "USERNAME" {
                        return a.Cred.Username
                }
                return os.Getenv(key)
        }

        for i, arg := range command {
                if i == 0 {
                        continue
                }
                // os.Expand substitutes $USERNAME with the attacker's input.
                // The result is treated as a shell script — no escaping is applied.
                command[i] = os.Expand(arg, envMapping)
        }

        // The shell will execute: sh -c "id ; echo injected"
        expectedArg := "id ; echo injected"
        if command[2] != expectedArg {
                t.Errorf("Expected command argument %q, got %q", expectedArg, command[2])
        }

        t.Logf("Confirmed: malicious username was injected as a shell script. Executing: %v", command)
}
```

## Remediation

Pass credentials exclusively as environment variables, not as shell string substitutions. This feature is undocumented, so removing it should not cause issues.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-m93h-4hw7-5qcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54088
- https://github.com/filebrowser/filebrowser
