# [H] Deposit function in TrueFiStrategy can do nothing and user lose the tfUSDC mint fee if tfFarm.getShare(tfUSDC) is 0, exposing himself to the risk by holding tfUSDC without yield.

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L88
Type: audit-issue

## Details
# Deposit function in TrueFiStrategy can do nothing and user lose the tfUSDC mint fee if tfFarm.getShare(tfUSDC) is 0, exposing himself to the risk by holding tfUSDC without yield.

## Summary

Deposit function in TrueFiStrategy can do nothing and user lose the tfUSDC mint fee if tfFarm.getShare(tfUSDC) is 0

## Vulnerability Detail

the deposit function is implemented below

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

if the share of tfUSDC in the farm is 0, the function will do nothing but return,

but inside the join function, a mint fee is charged when we use usdc to mint tfUSDC token

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L469

```solidity
        uint256 fee = amount.mul(joiningFee).div(BASIS_PRECISION);
        uint256 mintedAmount = mint(amount.sub(fee));
```

so if share of tfUSDC in the farm is 0, the user deposit the USDC, lose the mint fee and the tfUSDCs are not staked into the 
farm contract via

```solidity
tfFarm.stake(tfUSDC, tfUsdcBalance);
```

because the function return first.

holding tfUSDC without have yield is considered risky comparing to holding USDC.

## Impact

The user loss the mint fee and does not stake and enter the farm.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend project revert the transaction when the share tfUSDC is 0 to make sure the deposit is not succesfully
when the share of tfUSDC is 0.

```solidity
 tfUSDC.join(want.balanceOf(address(this)));
 if (tfFarm.getShare(tfUSDC) == 0) revert ZeroShares();
```
