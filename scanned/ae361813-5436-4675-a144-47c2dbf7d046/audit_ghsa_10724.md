# [C] Gemini CLI: Remote Code Execution via workspace trust and tool allowlisting bypasses

## Summary
Severity: Critical
Advisory: GHSA-wpqr-6v78-jr5g
CWE: CWE-20, CWE-200, CWE-77, CWE-78
Ecosystem: GitHub Actions, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-wpqr-6v78-jr5g
Type: github-advisory

## Affected
- npm: `@google/gemini-cli` — affected >=0 <0.39.1
- npm: `@google/gemini-cli` — affected >=0.40.0-preview.2 <0.40.0-preview.3
- GitHub Actions: `google-github-actions/run-gemini-cli` — affected >=0 <0.1.22

## Details
# Summary

Gemini CLI (`@google/gemini-cli`) and the `run-gemini-cli` GitHub Action are being updated to harden workspace trust and tool allowlisting, in particular when used in untrusted environments like GitHub Actions. This update introduces a breaking change to how non-interactive (headless) environments handle folder trust, which may impact existing CI/CD workflows under specific conditions.

# Details

Folder Trust in Headless Mode

In previous versions, Gemini CLI running in CI environments (headless mode) automatically trusted workspace folders for the purpose of loading configuration and environment variables. This is potentially risky in situations where Gemini CLI runs on untrusted folders in headless mode (e.g. CI workflows that review user-submitted pull requests). If used with untrusted directory contents, this could lead to remote code execution via malicious environment variables in the local `.gemini/` directory.

To ensure consistency and user control, the latest update aligns headless mode behavior with interactive mode, requiring folders to be explicitly trusted before configuration files (such as `.env`) are processed.

As a result of this change, GitHub Actions and other automated pipelines that rely on the previous automatic trust behavior will fail to load workspace-specific settings until they are updated to use explicit trust mechanisms.

Tool Allowlisting under \--yolo

In previous versions, when Gemini CLI was configured to run in `--yolo` mode, it would ignore any fine grained tool allowlist in `~/.gemini/settings.json` (e.g. `run_shell_command(echo)` would allow any command). This is potentially risky in situations where Gemini CLI runs on untrusted inputs with `--yolo` (e.g. CI workflows that triage user-submitted GitHub issues where we recommend a strict allowlist). If used with untrusted content and a tool allowlist that permits `run_shell_command`, this could lead to remote code execution via prompt injection.

In version `0.39.1`, the Gemini CLI policy engine now evaluates tool allowlisting under `--yolo` mode, which is useful for CI workflows that allowlist a few safe commands to run when processing untrusted inputs. As a result, some workflows that previously depended on this behavior may fail silently unless tool allowlists are modified to fit the task.

# Impact

This impact is limited to workflows using Gemini CLI in headless mode. Any use of Gemini CLI in headless mode without folder trust will require manual review to correctly configure folder trust. **This affects all Gemini CLI GitHub Actions.** Users must review their workflows, and take one of two approaches:

1\. If the workflow runs on trusted inputs (e.g. reviewing PRs from trusted collaborators), set `GEMINI_TRUST_WORKSPACE: 'true'` in your workflow.

2\. If the workflow runs on untrusted inputs, review our guidance in [google-github-actions/run-gemini-cli](https://github.com/google-github-actions/run-gemini-cli) to harden your workflow against malicious content, and set the environment variable.

# Patches

The folder trust and tool allowlisting mitigations are available in `@google/gemini-cli` version `0.39.1` and `0.40.0-preview.3`.  By default, the `run-gemini-cli` GitHub Action will receive and run the latest version of `gemini-cli`. However, if your workflow specifies a version of `gemini-cli` by setting the [gemini\_cli\_version](https://github.com/google-github-actions/run-gemini-cli#user-content-__input_gemini_cli_version), you are encouraged to upgrade to one of the patched versions and audit the workflow settings that use Gemini CLI.

# Credits

Gemini thanks the following security researchers for reporting this issue through the Vulnerability Rewards Program (g.co/vulnz):

* Elad Meged, Novee Security
* Dan Lisichkin, Pillar Security research team

## References
- https://github.com/google-github-actions/run-gemini-cli/security/advisories/GHSA-wpqr-6v78-jr5g
- https://github.com/google-github-actions/run-gemini-cli
