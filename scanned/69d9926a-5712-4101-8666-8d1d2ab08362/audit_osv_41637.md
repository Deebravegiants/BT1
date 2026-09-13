# [H] Omnigent: Unvalidated os_env.cwd in agent bundle yields arbitrary host filesystem access on runners without OMNIGENT_RUNNER_WORKSPACE

## Summary
Severity: High
Advisory: CVE-2026-62677
Aliases: GHSA-p8rw-8qj3-hf33, PYSEC-2026-3875
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62677
Type: osv

## Details
Omnigent is an open-source AI agent framework and meta-harness for orchestrating coding agents. Prior to 0.3.0, an authenticated user can upload a session-scoped agent bundle with an absolute or traversal-containing os_env.cwd value because omnigent/spec/parser.py stores the value verbatim and omnigent/spec/validator.py does not constrain it. On a runner where OMNIGENT_RUNNER_WORKSPACE is unset, omnigent/runner/resource_registry.py preserves the attacker-controlled path and omnigent/inner/os_env.py uses the resolved path as the environment root and copytree source. The _assert_within_cwd check then treats that attacker-selected root as trusted, allowing sys_os_read, write, edit, and shell tools to access runner files and environment secrets outside the intended workspace. This issue is fixed in version 0.3.0.

## References
- https://github.com/omnigent-ai/omnigent/releases/tag/v0.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62677.json
- https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-p8rw-8qj3-hf33
- https://nvd.nist.gov/vuln/detail/CVE-2026-62677
- https://github.com/omnigent-ai/omnigent/commit/7ca0cca3c9a65c04c489edf68f0e080424a26868
- https://github.com/omnigent-ai/omnigent/pull/1417
