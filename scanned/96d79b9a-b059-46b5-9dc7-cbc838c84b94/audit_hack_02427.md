# [M] Overflows in Fee Computation

## Summary
Severity: Medium
Source: https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L930
Type: audit-issue

## Details
The bootloader changes in scope involve a few formulas as part of the fee model, and there were a few instances where calculations were performed on user or operator-provided inputs. Unchecked arithmetic (without overflow protection) using these values is generally dangerous and prone to exploits.

One example is the calculated ergs price. If the `maxPriorityFeePerErg` is sufficiently large and the `maxFeePerErg` value is [increased to match](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L930), the [maxFeeThatOperatorCouldTake](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L944) calculation could overflow, resulting in a zero ergs price. The transaction will still be executed but the [amount the user pays](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L642) would be zero. A savvy operator could recognize this scenario and discard the operation, but it does make the system unnecessarily fragile.

We also identified the following cases where potential overflows with user-provided values appear to be unmitigated, although the consequences are limited:

* The [intrinsicOverhead](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L1024) calculation in the `getErgsLimitForTx` function
* The [return value](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L1457) of the `getBlockOverheadErgs` function
* The numerators of the `overheadForCircuits`, `overheadForLength`, and `overheadForPubdata` calculations in the [getTransactionUpfrontOverhead](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L1478) function

Lastly, the following functions appear to allow overflows, but they are protected by validations in other parts of the codebase:

* In [getBaseFee](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L90), a large `l1GasPrice` could cause `pubdataBytePriceETH` to overflow but the [validateOperatorProvidedPrices checks](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L34) prevent this.
* In [processL1Tx](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L813), `toRefundRecipient` would negative overflow if the value was too large, but the check on [line 1306](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L1306) prevents this.
* In [getErgsLimitForTx](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L1003), `ergsLimitForTx` would negative overflow if the `operatorOverheadForTransaction` was too large, but the check on [line 1253](https://github.com/matter-labs/system-contracts/blob/191246a878f1493a5ed5f0fa6d79af4ce3e7eb8f/bootloader/bootloader.yul#L1253) prevents this.

Consider applying additional checks to these operations, explicitly documenting where the checks are or why they would not be necessary. Whenever a potential overflow is not mitigated in the same function, consider documenting where the relevant validation can be found. It is advised to check the rest of the bootloader for more potential overflows and underflows. Lastly, it is recommended to validate all changes with proper dynamic testing.

_**Update:** Resolved in [pull request #211](https://github.com/matter-labs/system-contracts/pull/211) at commit [448932e](https://github.com/matter-labs/system-contracts/pull/211/commits/448932ec7d8797961919d74bbfbc1b074bec4efd)._
