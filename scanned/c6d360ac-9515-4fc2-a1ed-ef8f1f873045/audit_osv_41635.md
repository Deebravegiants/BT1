# [H] Omnigent: Uploaded Agent Bundle Allows Authenticated Runner RCE via Python Callable Tools

## Summary
Severity: High
Advisory: CVE-2026-62675
Aliases: GHSA-756x-9hf6-q4h4, PYSEC-2026-3872
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62675
Type: osv

## Details
Omnigent is an open-source AI agent framework and meta-harness for orchestrating coding agents. Prior to 0.3.0, multipart POST /v1/sessions accepts an authenticated user's agent bundle and omnigent/server/bundles.py validate_agent_bundle does not reject a tools..callable dotted Python path. omnigent/runner/tool_dispatch.py _resolve_spec_callable imports the specified module and _execute_spec_callable_tool invokes the resolved function, allowing a bundle to select subprocess.check_output and execute a local command with the runner process permissions. This can expose runner files, environment variables, credentials, workspace data, internal services, and availability without administrator access. This issue is fixed in version 0.3.0.

## References
- https://github.com/omnigent-ai/omnigent/releases/tag/v0.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62675.json
- https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-756x-9hf6-q4h4
- https://nvd.nist.gov/vuln/detail/CVE-2026-62675
- https://github.com/omnigent-ai/omnigent/commit/1f3f398f41cbf97b905133c21e848621c21da6e0
- https://github.com/omnigent-ai/omnigent/pull/1430
