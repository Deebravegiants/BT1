# [M] Tokens can be lost If the Join Fee is %100

## Summary
Severity: Medium
Reporter: defsec
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L90
Type: audit-issue

## Details
# Tokens can be lost If the Join Fee is %100

## Summary

On the TrueFi strategy, tfUSDC token is minted according to contract balance. However, If the TrueFi strategy sets fee as %100, all tokens can gone to fee.

## Vulnerability Detail

On the TrueFi strategy, tfUSDC token is minted according to contract balance. However, If the TrueFi strategy sets fee as %100, all tokens can gone to fee. In the `join` function of TrueFi, fee can be set to %100. In the Sherlock [contract](https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L90), there is no fee check. All token can be lost due to fee. 

## Impact

Strategy operation could not be completed.

## Code Snippet

https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L469

```solidity
    function setJoiningFee(uint256 fee) external onlyOwner {
        require(fee <= BASIS_PRECISION, "TrueFiPool: Fee cannot exceed transaction value");
        joiningFee = fee;
        emit JoiningFeeChanged(fee);
    }
```

## Tool used

Manual Review

## Recommendation

Consider check [fee](https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L70) is between pre-defined threshold.
