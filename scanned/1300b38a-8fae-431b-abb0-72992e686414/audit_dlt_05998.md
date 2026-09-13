# [?] fix(audit): more reentrancy checks (#1450)

## Summary
Severity: Unknown
Chain: EigenLayer
Component: Layr-Labs/eigenlayer-contracts
Published: 2025-06-11
Source: https://github.com/Layr-Labs/eigenlayer-contracts/commit/491a8e1b0a55fd51de81b2dd771c5149e92d2c0f
Type: security-commit

## Details
fix(audit): more reentrancy checks (#1450)

**Motivation:**

Release functions did not have a `nonReentrant` check, and while code is
well isolated it would be nice to prevent the concern entirely.

**Modifications:**

* Applied the `nonReentrant` modifier to both `releaseSlashEscrow` and
`releaseSlashEscrowByStrategy` functions within the `SlashEscrowFactory`
to prevent potential reentrancy vulnerabilities.

* Relocated the `nonReentrant` modifier from
`clearBurnOrRedistributableShares` to
`clearBurnOrRedistributableSharesByStrategy` in the `StrategyManager` to
ensure both methods are protected.

**Result:**

Less reentrancy-based security risk.
