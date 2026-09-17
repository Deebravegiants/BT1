# [M] pnpm: Git Fetch Argument Injection via Lockfile resolution.commit

## Summary
Severity: Medium
Advisory: GHSA-p4xf-rf54-rj3x
CVE: CVE-2026-50014
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-p4xf-rf54-rj3x
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.0
- npm: `pnpm` — affected >=11.0.0 <11.4.0

## Details
## Summary

pnpm passes the lockfile-controlled git `resolution.commit` value to `git fetch` without a `--` separator or commit-format validation. For git dependencies fetched through the shallow-fetch path, a malicious lockfile can replace the expected 40-character commit hash with a Git option such as `--upload-pack=<command>`. For SSH and local transports, `--upload-pack` can execute the supplied command. HTTPS transports ignore `--upload-pack`, so the practical attack surface is primarily SSH or local git dependencies.

## Vulnerability Details

The vulnerable path is in `fetching/git-fetcher/src/index.ts`. When a git dependency host is configured for shallow fetching, pnpm calls:

```typescript
await execGit(['fetch', '--depth', '1', 'origin', resolution.commit], { cwd: tempLocation })
```

Because `resolution.commit` is appended before a `--` separator, Git can parse a commit value beginning with `-` as an option. The same file later passes the value to `git checkout` without a separator:

```typescript
await execGit(['checkout', resolution.commit], { cwd: tempLocation })
```

`resolution.commit` comes from the lockfile and is typed as a plain `string`; pnpm does not validate it as a 40-character hexadecimal commit before passing it to Git.

## Proof of Concept

```bash
bash autofyn_audit/exploits/vuln11_git_upload_pack_rce/exploit.sh
# Creates a local bare git repo and triggers the shallow-fetch path.
# Replaces the lockfile commit hash with '--upload-pack=touch /tmp/vuln11_pwned'.
# Result: PASS -- /tmp/vuln11_pwned created by injected touch command.
```

The PoC uses a local `file://githost/...` repository because the injection requires a local or SSH transport. HTTPS transport ignores `--upload-pack`.

## Impact

Code execution as the user running `pnpm install`, under specific transport conditions. The attacker must modify `pnpm-lock.yaml`, and the affected dependency must use SSH or local git transport. HTTPS transport (the common case) is immune.

## Suggested Remediation

Add a `--` separator before lockfile-controlled git revision values. Validate `resolution.commit` matches `/^[0-9a-f]{40}$/i` before passing to Git.

---

> Discovered by [AutoFyn](https://github.com/SignalPilot-Labs/AutoFyn)
> Full audit report: [audit_report.md](https://github.com/tempcollab/pnpm/blob/main/autofyn_audit/audit_report.md)
> Exploit script: [exploit.sh](https://github.com/tempcollab/pnpm/blob/main/autofyn_audit/exploits/vuln11_git_upload_pack_rce/exploit.sh)

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-p4xf-rf54-rj3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-50014
- https://github.com/pnpm/pnpm
