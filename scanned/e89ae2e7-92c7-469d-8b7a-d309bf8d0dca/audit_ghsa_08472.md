# [H] Microsoft APM CLI's plugin.json component paths escape plugin root and copy arbitrary host files during install

## Summary
Severity: High
Advisory: GHSA-xhrw-5qxx-jpwr
CVE: CVE-2026-44641
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-xhrw-5qxx-jpwr
Type: github-advisory

## Affected
- PyPI: `apm-cli` — affected >=0 <0.8.12

## Details
### Summary
Microsoft APM normalizes marketplace plugins by copying plugin components referenced in `plugin.json` into `.apm/`. The manifest fields `agents`, `skills`, `commands`, and `hooks` are attacker-controlled, but the implementation does not enforce that those paths remain inside the plugin directory. A malicious plugin can therefore use absolute paths or `../` traversal paths to copy arbitrary readable host files or directories from the installer's machine during `apm install`.

In the verified primary proof of concept, a malicious plugin sets `plugin.json.commands` to an external markdown file. A single `apm install` copies that outside file into `.apm/prompts/` and then auto-integrates it into `.github/prompts/secret.prompt.md` in the victim project. This is a local supply-chain trust-boundary violation with direct confidentiality and integrity impact.

Reviewed version and commit:

- `apm-cli` version `0.8.11`
- `main` commit `70b34faa16a5a783424698163deeb028854fd23a`

### Details
Root cause:

- `src/apm_cli/deps/plugin_parser.py:336-348`
  - `_resolve_sources()` joins manifest-controlled `agents`, `skills`, `commands`, and directory-form `hooks` paths with `plugin_path`
  - it checks only `exists()` and `is_symlink()`
  - it does not resolve the candidate and verify containment inside the plugin root
- `src/apm_cli/deps/plugin_parser.py:356-395`
  - copies attacker-selected agent and skill files/directories into `.apm/`
- `src/apm_cli/deps/plugin_parser.py:397-452`
  - copies attacker-selected command and hook files/directories into `.apm/`
- `src/apm_cli/deps/plugin_parser.py:436-442`
  - string-form hook config paths are also copied without a root-containment check

There is already a safer precedent in the same module:

- `src/apm_cli/deps/plugin_parser.py:195-210`
  - `_read_mcp_file()` resolves the candidate path
  - rejects paths escaping the plugin root
  - rejects symlinks

Reachability:

- Local install path:
  - `src/apm_cli/commands/install.py:2007-2015`
  - local marketplace plugins are normalized through `normalize_plugin_directory(...)`
- Remote install path:
  - `src/apm_cli/deps/github_downloader.py:2224-2230`
  - downloaded packages are validated through `validate_apm_package(target_path)`
  - `src/apm_cli/models/validation.py:164-172`, `224-226`, `304-324`
  - marketplace plugins are normalized through the same vulnerable path after clone

Project write-back path:

- `src/apm_cli/integration/prompt_integrator.py:38-56`
  - reads `.apm/prompts/*.prompt.md`
- `src/apm_cli/integration/prompt_integrator.py:170-189`
  - writes prompt files into `.github/prompts/`
- `src/apm_cli/commands/install.py:2496-2514`
  - auto-integrates package primitives after install

This means a malicious dependency can cause APM to read from outside the dependency itself and materialize host-local content into managed install output and, in the verified prompt case, directly into the victim project.

### PoC
The attached zip contains a complete maintainer-ready proof-of-concept package, including runnable scripts, payload templates, captured output, and the exact validation environment.

Primary end-to-end `apm install` reproduction:

1. Install APM from the reviewed source tree (`apm-cli 0.8.11`, commit `70b34faa16a5a783424698163deeb028854fd23a`) into a Python environment.
2. Create an external file outside the malicious plugin directory, for example:

```text
victim\secret.md
```

with content:

```md
# STOLEN VIA APM INSTALL
```

3. Create a malicious plugin with this minimal `plugin.json`:

```json
{
  "name": "evil-plugin",
  "commands": "D:\\absolute\\path\\to\\victim\\secret.md"
}
```

4. Create a minimal `apm.yml` that references the malicious plugin.
5. Run:

```powershell
apm install
```

6. Observe that APM completes successfully and writes:

```text
.github/prompts/secret.prompt.md
```

7. Observe that the resulting prompt file contains the external host file content:

```md
# STOLEN VIA APM INSTALL
```

Verified console output from the included PoC:

```text
[>] Installing dependencies from apm.yml...
  [+] ./evil-plugin (local)
  |-- 1 prompts integrated -> .github/prompts/

[*] Installed 1 APM dependency.
PoC succeeded.
Integrated into project: ...\.github\prompts\secret.prompt.md
Integrated content:
# STOLEN VIA APM INSTALL
```

Secondary remote-parity reproduction:

- The attached `reproduce-remote-parity.py` exercises `GitHubPackageDownloader.download_package(...)` after clone by replacing only the clone callback to keep the test self-contained.
- It confirms the same unsafe normalization path copies an outside host file into:

```text
<download-target>/.apm/prompts/secret.prompt.md
```

### Impact
This is a path traversal / arbitrary local file copy issue in the package install flow.

Who is impacted:

- any user who runs `apm install` against a malicious or compromised plugin dependency
- both direct and transitive dependency consumers

What an attacker gains:

- ability to copy arbitrary readable host files into `.apm/` during install
- ability to copy arbitrary readable host directories recursively into `.apm/`
- ability to trigger project write-back when the copied content lands in supported primitive locations such as `.apm/prompts/`

Practical impact:

- local notes, markdown, source material, or configuration files can be staged into repository-controlled paths
- copied prompt files are automatically written into `.github/prompts/`, increasing the chance that sensitive or attacker-selected content is committed, synced, or consumed by other tooling
- the issue breaks the expected trust boundary that a dependency install should copy only content belonging to the dependency itself

### Mitigation
Recommended fix:

1. Resolve every manifest-controlled component path against `plugin_path.resolve()`.
2. Reject absolute or relative paths that escape the plugin root.
3. Apply the same containment check to `agents`, `skills`, `commands`, and both `hooks` code paths.
4. Reject symlinks before copying.
5. Add regression tests for:
   - absolute file path in `commands`
   - absolute directory path in `commands`
   - `../` traversal in `agents`
   - `../` traversal in `skills`
   - `../` traversal in `hooks`
   - confirmation that only in-root files remain accepted

### Attachment
[Microsoft_APM_Plugin_Path_Escape_Report_Final.zip](https://github.com/user-attachments/files/26829524/Microsoft_APM_Plugin_Path_Escape_Report_Final.zip)

## References
- https://github.com/microsoft/apm/security/advisories/GHSA-xhrw-5qxx-jpwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44641
- https://github.com/microsoft/apm
