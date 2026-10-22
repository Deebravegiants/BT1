# [H] \[H05\] Incorrect gas price \[core\]

## Summary
Severity: High
Source: https://github.com/eth-infinitism/account-abstraction/blob/8832d6e04b9f4f706f612261c6e46b3f1745d61a/contracts/UserOperation.sol#L34-L38
Type: audit-issue

## Details
**Client reported:** _The Ethereum Foundation identified this issue during the audit._

The gas price to charge the user (potentially through the paymaster) for the operation is [calculated](https://github.com/eth-infinitism/account-abstraction/blob/8832d6e04b9f4f706f612261c6e46b3f1745d61a/contracts/UserOperation.sol#L34-L38) as the minimum of the transaction gas price and the user-specified gas price (after accounting for any `basefee`). However, the user should always pay their specified price so the bundler can receive the excess, which provides the incentive to process the user operation in the first place. Consider allowing the user’s gas price to exceed the transaction gas price.

_**Update**: Fixed in pull request [#55](https://github.com/eth-infinitism/account-abstraction/pull/55/files). The `tx.gasprice` value has been removed from the gas price calculation._
