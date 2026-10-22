# [H] TrueFi double loan

## Summary
Severity: High
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L88
Type: audit-issue

## Details
# TrueFi double loan

## Summary

Although TrueFi has KYC on the entity, the on chain loan and off chain are separate. If the company apply for a loan through TrueFi, and at the same time, apply for another loan off chain, before the loan is released and shown up on the balance sheet, it is not likely to be known. If both loan get approved, the company might be under collateralized. If a company conducts something like this, it is likely they do it on purpose to cheat for the loan and default later.

## Vulnerability Detail

A whitelisted company can try to apply to loans in parallel for on chain and off chain. The 2 process are kind of isolated to each other. Hence is it possible to get loan amount much more than suppose to.

## Code Snippet

## Impact

When a company apply for loans on chain and off chain in parallel, and later default, the contract will suffer loss. Due to the off chain legal process might not put on chain contracts on priority.

## Code Snippet

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L88

```solidity
  function _deposit() internal override whenNotPaused {
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L469
    tfUSDC.join(want.balanceOf(address(this)));

    // Don't stake in the tfFarm if shares are 0
    // This would make the function call revert
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueMultiFarm.sol#L101
    if (tfFarm.getShare(tfUSDC) == 0) return;

    // How much tfUSDC is in this contract
    // Could both be tfUSDC that was already in here before the `_deposit()` call
    // And new tfUSDC that was minted in the `tfUSDC.join()` call
    uint256 tfUsdcBalance = tfUSDC.balanceOf(address(this));

    // Stake all tfUSDC in the tfFarm
    tfFarm.stake(tfUSDC, tfUsdcBalance);
  }
```


## Tool used

Manual Review

## Recommendation

Purchase on chain insurance against TrueFi loss.
