# [?] fix(prover): Fix panics if prover's config is not ready (#1822)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-04-29
Source: https://github.com/matter-labs/zksync-era/commit/21d90d766798fb05be95028df185e9036ec7dee9
Type: security-commit

## Details
fix(prover): Fix panics if prover's config is not ready (#1822)

Prover config caused an outage before.
As part of that change, we made prover configs return an error, rather
than panic.
Whilst this helped, there are still a few edge cases where things can go
wrong.
One of them is when we add aggregation rounds.
This commit addresses the panics, turning them into an error.
