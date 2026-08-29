# [M] `AtomWallet.execute()` should be `payable`

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-21
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/2
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xc83076d185673fc7adc2ae0e837defccab7b394a2652dc20037633a48b506cc8
**Severity:** medium

**Description:**
In `AtomWallet.execute()` contract, `execute()` is used to execute a transaction which is either called from owner or entryPoint. 

```solidity
    function execute(address dest, uint256 value, bytes calldata func) external onlyOwnerOrEntryPoint {
@>      _call(dest, value, func);         @audit // value is non-zero means ether is expected to be send along with function
    }
```

`execute()` function takes `value` as a param and part of transaction call. The `value` is the `ethers` which are sent along with function call. `execute()` calls internal function `_call()` for the transactions execution which is implemented as below:

```solidity
    function _call(address target, uint256 value, bytes memory data) internal {
@>      (bool success, bytes memory result) = target.call{value: value}(data);
        if (!success) {
            assembly {
                revert(add(result, 32), mload(result))
            }
        }
    }
```

It can be seen at (@), the ether value is indeed a part of `execute()` function as the **value is not hardcoded to 0**.

Now, the issue is that, `execute()` will revert when msg.value > 0. The current implementation of the `execute()` function within the smart contract lacks the `payable` keyword. This omission leads to a critical issue where any transaction that attempts to send ether (ETH) to this function or with call of this function will fail. 

Since the function is designed to allow the owner to execute transaction calls and potentially send ETH, the inability to accept ETH due to the missing payable specifier means that:

1) The contract does not behave as intended when interacting with functions or operations requiring ETH transfers via `execute()`
2) Any attempt to send ETH to `execute()` function will revert and result in a failure of the intended operation.
3) ETH sent to this non-payable function will be stuck and effectively lost, leading to financial losses for the function callers.

**Impact Details**\

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/2_
