# [?] docs: add security vulnerability disclosure policy (#8978)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-05
Source: https://github.com/fedimint/fedimint/commit/fbc127fe1f4b94da9d670c1f2706ef9dcdddaafc
Type: security-commit

## Details
docs: add security vulnerability disclosure policy (#8978)

### Summary

Adds a root `SECURITY.md` establishing a private vulnerability
disclosure channel. Until now the repo had no security policy anywhere,
so anyone finding a vulnerability had no sanctioned option besides a
public issue.

### Details

Reports go to **security@fedimint.org** (forwards to dpc and elsirion)
or to `@elsirion.21` on Signal. For sensitive reports the policy lists
both maintainers' PGP key fingerprints and how to fetch the keys from
the Proton key server. It also states supported versions (latest stable
release line only) and scopes out threshold-guardian collusion and bugs
in third-party dependencies. It deliberately makes no process or SLA
commitments.

### Reviewing

- @dpc please confirm your listed key fingerprint (`23B8 147B 42EB 74CB
801F F76F 930E AF17 AB8F F29C`) and that security@fedimint.org
forwarding reaches you.
- GitHub private vulnerability reporting is currently disabled on this
repo; we could enable it and list it as an additional channel, but the
policy works without it.

### Testing

Docs-only change; `just final-lint` passes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01BLtSHuk4w9fecCsn5CP7c1
