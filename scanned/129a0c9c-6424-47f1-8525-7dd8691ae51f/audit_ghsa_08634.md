# [M] Vercel: Non-interactive mode includes CLI arguments in suggested command output

## Summary
Severity: Medium
Advisory: GHSA-pgf8-2hgj-grqg
CVE: CVE-2026-44479
CWE: CWE-200, CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-pgf8-2hgj-grqg
Type: github-advisory

## Affected
- npm: `vercel` — affected >=50.16.0 <52.0.1

## Details
# Summary

When the Vercel CLI runs in non-interactive mode (`--non-interactive` or auto-detected AI agent), commands that cannot complete autonomously emit JSON payloads with suggested follow-up commands. If the user authenticated via `--token` or `-t` on the command line, the token value is included verbatim in those suggestions.

# Conditions

All three must be true for the token to appear in output:

1. Token passed as a CLI argument (`--token` / `-t`). The `VERCEL_TOKEN` environment variable is **not affected**.
2. Non-interactive mode is active (explicit flag or AI agent auto-detection).
3. The command cannot complete on its own (e.g. missing `--yes`, ambiguous scope, API errors). Successful commands produce no suggestion output.

## Impact

The plaintext token may be captured in CI/CD logs, agent transcripts, or other automation output.

## Remediation

- Upgrade to the patched version.
- If developers have previously used `--token` with `--non-interactive` in their applications, review logs for exposed tokens and rotate them.
- Prefer `VERCEL_TOKEN` environment variable for authentication.

## References
- https://github.com/vercel/vercel/security/advisories/GHSA-pgf8-2hgj-grqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44479
- https://github.com/vercel/vercel
