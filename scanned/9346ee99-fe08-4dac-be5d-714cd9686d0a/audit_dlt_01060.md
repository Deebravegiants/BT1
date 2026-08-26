# [M] nimiq-account: Vesting insufficient funds error can panic

## Summary
Severity: Medium
Chain: nimiq-account
Component: nimiq-account
CVE: CVE-2026-34064
CWE: Integer Underflow (Wrap or Wraparound)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-vc34-39q2-m6q3
Type: github-advisory

## Details
### Impact
`VestingContract::can_change_balance` returns `AccountError::InsufficientFunds` when `new_balance < min_cap`, but it constructs the error using `balance: self.balance - min_cap`. `Coin::sub` panics on underflow, so if an attacker can reach a state where `min_cap > balance`, the node crashes while trying to return an error.

The `min_cap > balance` precondition is attacker-reachable because the vesting contract creation data (32-byte format) allows encoding `total_amount` without validating `total_amount <= transaction.value` (the real contract balance). After creating such a vesting contract, the attacker can broadcast an outgoing transaction to trigger the panic during mempool admission and block processing.

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/commit/4d01946f0b3d6c6e31786f91cdfb3eb902908da0) is included as part of [v1.3.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0).

### Workarounds
No known workarounds.
