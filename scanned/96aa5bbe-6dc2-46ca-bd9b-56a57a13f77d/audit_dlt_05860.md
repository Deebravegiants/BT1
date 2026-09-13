# [?] chore(rust): ignore RUSTSEC-2026-0118 and RUSTSEC-2026-0119 (#20514)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-05-04
Source: https://github.com/ethereum-optimism/optimism/commit/742987c5fae7fe9574d96296c9738e6a532250a3
Type: security-commit

## Details
chore(rust): ignore RUSTSEC-2026-0118 and RUSTSEC-2026-0119 (#20514)

Both advisories were published 2026-05-01 and affect hickory-proto
<0.26.1, pulled in transitively via reth-network ->
reth-dns-discovery. Ignore in deny.toml until an upstream bump lands.

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
