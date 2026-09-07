# [H] PySpector has a Plugin Sandbox Bypass leads to Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-v3xv-8vc3-h2m6
CVE: CVE-2026-33139
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-v3xv-8vc3-h2m6
Type: github-advisory

## Affected
- PyPI: `pyspector` — affected >=0 <0.1.7

## Details
### Summary
PySpector versions `<= 0.1.6` are affected by a security validation bypass in the plugin system. The `validate_plugin_code()` function in `plugin_system.py`, performs static AST analysis to block dangerous API calls before a plugin is trusted and executed. However, the `internal resolve_name()` helper only handles `ast.Name` and `ast.Attribute` node types, returning `None` for all others. When a plugin uses indirect function calls via `getattr()` (such as `getattr(os, 'system')`) the outer call's func node is of type `ast.Call`, causing `resolve_name()` to return `None`, and the security check to be silently skipped. The plugin incorrectly passes the trust workflow, and executes arbitrary system commands on the user's machine when loaded.

### Impact
An attacker who can deliver a malicious plugin file to a PySpector user and convince them to install it, can achieve arbitrary code execution on the user's local machine. Exploitation requires the victim to explicitly run `pyspector plugin install --trust` on the malicious file (a deliberate multi-step action that meaningfully limits the attack surface compared to passive vulnerabilities). However, the bypass directly undermines the security guarantee that `validate_plugin_code()` is designed to provide. Once the plugin is trusted and executed, the following is achievable:
- Full read/write access to the local filesystem
- Exfiltration of sensitive data and environment variables (i.e. API keys, credentials, etc...)
- Establishment of persistence mechanisms
- Lateral movement in CI/CD environments where PySpector runs with elevated permissions (pre-commit hooks and scheduled scans)

Any user of PySpector who installs third-party plugins outside the official repository is potentially affected.

### PoC
The following steps reproduce the vulnerability on PySpector `<= 0.1.6`:
1. Create a malicious plugin file that uses getattr-based indirect calls to bypass AST validation, and confirm the validator incorrectly marks it as safe:
<img width="1300" height="675" alt="image" src="https://github.com/user-attachments/assets/4de3a0d1-1c77-4454-ad10-2369d5ca9997" />
2.  Run PySpector Plugin Validator module (this confirms the validator incorrectly marks the plugin as safe):
<img width="908" height="239" alt="image" src="https://github.com/user-attachments/assets/3e3b9603-4d95-4a39-be97-4163f6639599" />
3. Install and trust the plugin through the normal PySpector workflow:

`pyspector plugin install /tmp/evil_plugin.py --trust`
4. Execute the plugin, during a scan:
`pyspector scan /any/target --plugin evil`

## References
- https://github.com/ParzivalHack/PySpector/security/advisories/GHSA-v3xv-8vc3-h2m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33139
- https://github.com/ParzivalHack/PySpector
