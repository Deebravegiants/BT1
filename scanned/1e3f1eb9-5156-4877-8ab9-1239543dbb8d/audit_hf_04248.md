# [M] Function `Pool.validateOffer`

## Summary
Severity: Medium
Contest weight: 0.6131
Dataset id: 21171
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Pool contract, undeployed funds could be deposited to Aave or Lido to earn base yield. When an offer of Pool is accepted from `MultiSourceLoan`, the function `validateOffer()` is called to validate the terms and also to pull the undeployed funds back in case the contract balance is insufficient.

```solidity
if (principalAmount > undeployedAssets) {
    revert InsufficientAssetsError();
} else if (principalAmount > currentBalance) {
    IBaseInterestAllocator(getBaseInterestAllocator).reallocate(
        currentBalance, principalAmount - currentBalance, true // @audit Incorrect
    );
}
```

However, the input params of `reallocate()` are incorrect, resulting in the contract balance might still be insufficient for the loan after calling the function.

## Proof of Concept
Consider the scenario:

  1. Assume we have `currentBalance = 500`, `baseRateBalance = 1000 usdc` and `principalAmount = 700 usdc`.
  2. Since the current contract balance is insufficient (500 `<` 700), `reallocate()` will be called with input:

    reallocate(currentBalance, principalAmount - currentBalance, true)
    reallocate(500, 200, true)

  3. In function `reallocate()` shown in the code snippet below, we can see that in case `_currentIdle > _targetIdle`, the contract even deposits more funds to `AavePool` instead of withdrawing.

```solidity
function reallocate(uint256 _currentIdle, uint256 _targetIdle, bool) external {
    address pool = _onlyPool();
    if (_currentIdle > _targetIdle) {
        uint256 delta = _currentIdle - _targetIdle;
        ERC20(_usdc).transferFrom(pool, address(this), delta);
        IAaveLendingPool(_aavePool).deposit(_usdc, delta, address(this), 0);
    } else {
        uint256 delta = _targetIdle - _currentIdle;
        IAaveLendingPool(_aavePool).withdraw(_usdc, delta, address(this));
        ERC20(_usdc).transfer(pool, delta);
    }

    emit Reallocated(_currentIdle, _targetIdle);
}
```

## Recommendation
Call `reallocate(0, principalAmount - currentBalance, true)` instead.

If I understand correctly, the impact is DoS that occurs only under certain conditions; in that case, I think severity should be Medium.

Agree on the issue. I think it’s Medium, not High.

Changed to reallocate (`currentBalance`, `principalAmount`, true) instead of proposed solution (same result) to be compliant with the interface.
