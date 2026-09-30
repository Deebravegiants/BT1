# [H] Wrangler affected by OS Command Injection in `wrangler pages deploy`

## Summary
Severity: High
Advisory: GHSA-36p8-mvp6-cv38
CVE: CVE-2026-0933
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-36p8-mvp6-cv38
Type: github-advisory

## Affected
- npm: `wrangler` — affected >=2.0.15 <3.114.17
- npm: `wrangler` — affected >=4.0.0 <4.59.1

## Details
**Summary**

A command injection vulnerability (CWE-78) has been found to exist in the `wrangler pages deploy` command. The issue occurs because the `--commit-hash` parameter is passed directly to a shell command without proper validation or sanitization, allowing an attacker with control of `--commit-hash` to execute arbitrary commands on the system running Wrangler.

**Root cause**

The `commitHash` variable, derived from user input via the `--commit-hash` CLI argument, is interpolated directly into a shell command using template literals (e.g., ``execSync(`git show -s --format=%B ${commitHash}`)``). Shell metacharacters are interpreted by the shell, enabling command execution.

**Impact**

This vulnerability is generally hard to exploit, as it requires `--commit-hash` to be attacker controlled. The vulnerability primarily affects CI/CD environments where `wrangler pages deploy` is used in automated pipelines and the `--commit-hash` parameter is populated from external, potentially untrusted sources. An attacker could exploit this to:

- Run any shell command.
- Exfiltrate environment variables.
- Compromise the CI runner to install backdoors or modify build artifacts.

**Mitigation**

- Wrangler v4 users are requested to upgrade to Wrangler v4.59.1 or higher. 
- Wrangler v3 users are requested to upgrade to Wrangler v3.114.17 or higher. 
- Users on Wrangler v2 (EOL) should upgrade to a supported major version.

**Credits**

Disclosed responsibly by kny4hacker.

## References
- https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-36p8-mvp6-cv38
- https://nvd.nist.gov/vuln/detail/CVE-2026-0933
- https://github.com/cloudflare/workers-sdk/commit/99b1f328a9afe181b49f1114ed47f15f6d25f0be
- https://github.com/cloudflare/workers-sdk
- https://github.com/cloudflare/workers-sdk/releases/tag/wrangler%403.114.17
- https://github.com/cloudflare/workers-sdk/releases/tag/wrangler%404.59.1
