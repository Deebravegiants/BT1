# [M] `EulerStrategy._withdraw()` doesn't use the balance of `USDC` in the contract.

## Summary
Severity: Medium
Reporter: hansfriese
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L51
Type: audit-issue

## Details
# `EulerStrategy._withdraw()` doesn't use the balance of `USDC` in the contract.

## Summary
`EulerStrategy._withdraw()` doesn't use the balance of `USDC` in the contract.

As a result, the contract would force to withdraw `eUSDC` needlessly.


## Vulnerability Detail
As we can see from [_deposit()](https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L51), this contract should have some `USDC` before calling `_deposit()`.

So the below scenario would be possible.
- A user(admin or parent) transferred 50 `USDC` to this contract and called `_deposit()` function successfully.
- After a few days, he transferred another 100 `USDC` to deposit again.
- Before calling the second `_deposit()`, the contract was paused for some reason and he can't call `_deposit()` because of the `whenNotPaused` modifier.
- He wants to withdraw his 100 `USDC` back without touching the already deposited 50 `USDC`.
- But [_withdraw(100)](https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L77) will revert because this function doesn't consider the balance of `USDC` in the contract and he deposited 50 `USDC` only.
- So he should call `_withdrawAll()` and all of 150 `USDC` will be withdrawn although he wanted to withdraw 100 `USDC`.


## Impact
`EulerStrategy._withdraw()` wouldn't work properly when the contract has some balance of `USDC`.

It might withdraw the `eUSDC` when it shouldn't.


## Code Snippet
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L77


## Tool used
Solidity Visual Developer of VSCode


## Recommendation
We should modify `_withdraw()` like below.

```
function _withdraw(uint256 _amount) internal override {
    // Don't allow to withdraw max (reserved with withdrawAll call)
    if (_amount == type(uint256).max) revert InvalidArg();

    uint256 usdcAmount = want.balanceOf(address(this));

    if(_amount > usdcAmount) {
        // Call withdraw with underlying amount of tokens (USDC instead of eUSDC)
        // https://github.com/euler-xyz/euler-contracts/blob/master/contracts/modules/EToken.sol#L177
        EUSDC.withdraw(SUB_ACCOUNT, _amount - usdcAmount);
    }

    // Transfer USDC to core
    want.safeTransfer(core, _amount);
}
```
