# [M] transfer functions does not check token existence

## Summary
Severity: Medium
Chain: Smart contract
Component: Accumulated-finance
Published: 2024-09-05
Source: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/51
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x15b630ae5bf5716a266e18fa85f7902cf84b81065b45b018c932b40bba938fa4
**Severity:** medium

**Description:**
**Description**\
The AccumulatedFi contracts(inscope as well as out of scope) have used `SafeTransferLib` library which is take from Solmate as referenced [here](https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/blob/fea3cdcd7693e95c7ddcfa4c79df9b5fa715aafc/contracts/Minter.sol#L290) in `Minter.sol`.

The issue is with [safeTransfer()](https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/blob/fea3cdcd7693e95c7ddcfa4c79df9b5fa715aafc/contracts/Minter.sol#L346-L375) and [safeTransferFrom()](https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/blob/fea3cdcd7693e95c7ddcfa4c79df9b5fa715aafc/contracts/Minter.sol#L313-L344) functions which is extensively used across AccumulatedFi contracts and also in Minter.sol.

The used `safeTransfer()` and `safeTransferFrom()` function from solmate library doesn't check the existence of code at the token address. This is a known issue while using solmate's libraries.

As Per Natspec in `Minter.sol` which can be checked [here](https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/blob/fea3cdcd7693e95c7ddcfa4c79df9b5fa715aafc/contracts/Minter.sol#L292)

> Note that none of the functions in this library check that a token has code at all! .....

Hence using safeTransferLib.sol library may lead to miscalculation of funds and may lead to loss of funds , because if `safeTransferFrom()` are called on a token address that **doesn't have contract** in it, it will always return success, bypassing the return value check. Due to this protocol will think that funds has been transferred to recipient address and the transaction would be successful, and records will be accordingly calculated, but in reality funds were never been transferred.

`safeTransferFrom()` and `safeTranfer()` function under the hood uses low level call function which can be checked [here](https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/blob/fea3cdcd7693e95c7ddcfa4c79df9b5fa715aafc/contracts/Minter.sol#L339) and [here](https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/blob/fea3cdcd7693e95c7ddcfa4c79df9b5fa715aafc/contracts/Minter.sol#L370)

```solidity
                call(gas(), token, 0, freeMemoryPointer, 68, 0, 32)
```

However, solidity documentation strictly warns that,

> The low-level functions call, delegatecall and staticcall return true as their first return value if the account called is non-existent, as part of the design of the EVM. Account existence must be checked prior to calling if needed.

code existence must be checked especially for low level functions like call,staticcall and delegatecall.

`Openzeppelin` and `Solady` confirms this and comply this requirements in their libraries, only currently used solmate does not check code existence.

**Recommendation**\
Recommended to use openzeppelin's safeERC20 which takes care of token code existence OR alternatively check code existence as shown below:

```diff
    function safeTransferFrom(
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/51_
