# [?] chore(rust): ignore RUSTSEC-2026-0173 (proc-macro-error2 unmaintained) (#21274)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-06-08
Source: https://github.com/ethereum-optimism/optimism/commit/47d898adfb4de58a3fbad6ade582d73650964350
Type: security-commit

## Details
chore(rust): ignore RUSTSEC-2026-0173 (proc-macro-error2 unmaintained) (#21274)

proc-macro-error2 is flagged unmaintained by RUSTSEC-2026-0173 (no
vulnerability, no patched release exists). It is a build-time-only proc-macro
dependency pulled in via alloy-sol-macro; the latest alloy-core (1.6.0) and its
main branch still pin it because they use a private API, so no upgrade removes
it. Add a scoped advisory ignore matching the existing unmaintained/transitive
ignores in deny.toml.
