# [M] Unchecked subtraction underflow

## Summary
Severity: Medium
Source: https://github.com/matter-labs/zksync-2-contracts/blob/3f345ce52bc378c4b5d710c80d817db170775049/ethereum/contracts/zksync/facets/Mailbox.sol#L543
Type: audit-issue

## Details
L2 gas validation performs [an unchecked subtraction](https://github.com/matter-labs/zksync-2-contracts/blob/3f345ce52bc378c4b5d710c80d817db170775049/ethereum/contracts/zksync/facets/Mailbox.sol#L543), and a neighboring comment states that the underflow prevention is enforced by the implementation of the preceding computation. However, the preceding computation takes a large variety of constants and variable parameters, which depending on their values can still cause an underflow.

For example, the calculation of the memory overhead can result in arbitrarily large values depending on the value passed in `_encodingLength` and the constant `BOOTLOADER_TX_ENCODING_SPACE`, since both values’ ranges are not validated.

Note that it is likely that there are additional ways by which the combination of different possible values of constants and inputs could cause the resulting overhead to be higher than the total gas limit.

This may result in an underflow of the unchecked subtraction. In turn, it will likely cause a revert due to subsequent [l2GasForTxBody](https://github.com/matter-labs/zksync-2-contracts/blob/3f345ce52bc378c4b5d710c80d817db170775049/ethereum/contracts/zksync/facets/Mailbox.sol#L346-L348) checks.

Consider not using the `unchecked` subtraction to prevent the underflow, and adding an explicit check to validate the overhead.

_**Update:** Resolved in [pull request #54](https://github.com/matter-labs/zksync-2-contracts/pull/54) at commit [94bc1a6](https://github.com/matter-labs/zksync-2-contracts/pull/54/commits/94bc1a679cd55afb0929c33ff47d27911ab55a6f)._
