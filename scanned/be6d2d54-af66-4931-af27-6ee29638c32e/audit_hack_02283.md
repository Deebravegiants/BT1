# [H] \[H01\] Incorrect prefund calculation \[core\]

## Summary
Severity: High
Source: https://github.com/eth-infinitism/account-abstraction/blob/8832d6e04b9f4f706f612261c6e46b3f1745d61a/contracts/UserOperation.sol#L46
Type: audit-issue

## Details
In order to ensure a user operation can be financed, the maximum amount of gas it could consume is calculated. This depends on the individual gas limits specified in the transaction. Since the paymaster may use `verificationGas` to limit up to three function calls, operations that have a paymaster should multiply `verificationGas` by 3 when calculating the maximum gas. However, the [calculation is inverted](https://github.com/eth-infinitism/account-abstraction/blob/8832d6e04b9f4f706f612261c6e46b3f1745d61a/contracts/UserOperation.sol#L46). This means that valid user operations could fail in two ways:

* Operations that do not rely on paymasters will be initially overcharged, and the wallet may have insufficient funds to proceed. It should be noted that wallets with sufficient funds will still have any unused gas (including the overcharge) refunded after the operation is executed.
* Paymasters that are insufficently staked may nevertheless pass validation, which introduces the possibility that they will be unable to fund the operation. In practice, the excess funds will probably simply be deducted from their stake. Even so, this allows users to craft operations that would unexpectedly cause the paymaster to become unstaked.

Consider updating the maximum gas calculation to match the execution behavior.

_**Update**: Fixed in pull request [#51](https://github.com/eth-infinitism/account-abstraction/pull/51/files)._
