# [M] PySpector has a Plugin Code Execution Bypass via Incomplete Static Analysis in PluginSecurity.validate_plugin_code

## Summary
Severity: Medium
Advisory: GHSA-vp22-38m5-r39r
CVE: CVE-2026-41206
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-vp22-38m5-r39r
Type: github-advisory

## Affected
- PyPI: `pyspector` — affected >=0 <0.1.8

## Details
### Summary

The plugin security validator in PySpector uses AST-based static analysis to prevent dangerous code from being loaded as plugins. The blocklist implemented in `PluginSecurity.validate_plugin_code` is incomplete and can be bypassed using several Python constructs that are not checked. An attacker who can supply a plugin file can achieve arbitrary code execution within the PySpector process when that plugin is installed and executed.

### Details

The validator maintains a set called `fatal_calls` that enumerates explicitly forbidden function names and attribute access patterns such as eval, exec, `os.system`, and `subprocess.Popen`. However, this approach relies on an exhaustive blocklist of known-dangerous identifiers, which is inherently incomplete.

The following bypass techniques are not detected by the current implementation:

`importlib.import_module` is not in `fatal_calls` and is not treated as a dangerous module, so it can be used to load os, subprocess, or any other module at runtime without triggering the validator.

Dynamic attribute chains using `__class__.__mro__` and related dunder attributes allow traversal of the class hierarchy to reach arbitrary built-in functions without naming them directly in the source.

ctypes is not blocked and can be used to call native library functions including system.

`__builtins__` dictionary access exposes all built-in callables without using the names that the validator checks.

`types.CodeType` allows construction and execution of raw code objects.

The alias resolution in the AST visitor only handles simple import X as Y cases, so aliased imports of blocked modules evade detection, and transitive imports through unblocked modules are never examined.

Because the validator produces a pass/fail result that gates plugin installation with the --trust flag, a bypass causes untrusted plugin code to execute with the full privileges of the PySpector process.

### PoC

```python
import textwrap, tempfile, os

evil_plugin = textwrap.dedent("""
import importlib
mod = importlib.import_module('os')
mod.system('id > /tmp/pwned')
""")

with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
    f.write(evil_plugin)
    plugin_path = f.name

from pyspector.plugin_system import PluginSecurity

result = PluginSecurity.validate_plugin_code(plugin_path)
print("Validation passed:", result)

exec(compile(open(plugin_path).read(), plugin_path, "exec"))

print("Command output:", open("/tmp/pwned").read())
os.unlink(plugin_path)
```

### Impact

Any user or process that can supply a plugin file to PySpector and invoke the plugin installation workflow can execute arbitrary operating system commands with the privileges of the PySpector process. The static analysis check provides a false sense of security, as it can be circumvented trivially using standard library modules that are present in every Python installation. All versions of PySpector that include the plugin system are affected.

## References
- https://github.com/ParzivalHack/PySpector/security/advisories/GHSA-vp22-38m5-r39r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41206
- https://github.com/ParzivalHack/PySpector/commit/3c9547157fc07396f22b26b3484a9a91eba98555
- https://github.com/ParzivalHack/PySpector/commit/4e279e078c53d760fd321ff9b698d683c65ccb8e
- https://github.com/ParzivalHack/PySpector
