# [M] It is possible that the USDC amount, which is accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract and is not designated for investing in the corresponding strategy, is deposited to the relevant Euler's or TrueFi's contract

## Summary
Severity: Medium
Reporter: rbserver
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L51-L55
Type: audit-issue

## Details
# It is possible that the USDC amount, which is accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract and is not designated for investing in the corresponding strategy, is deposited to the relevant Euler's or TrueFi's contract

## Summary
The USDC amount, which is accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract and is not designated for investing in the corresponding strategy, can be deposited to the relevant Euler's or TrueFi's contract.

## Vulnerability Detail
When calling the `EulerStrategy._deposit` or `TrueFiStrategy._deposit` function, which is shown in the Code Snippet section, the `EulerStrategy` or `TrueFiStrategy` contract's USDC balance at that moment is transferred to the relevant Euler's or TrueFi's contract. If some USDC amount is accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract before such function is called, such amount is included in the contract's USDC balance and will be deposited when such function is called. Therefore, although such amount is accidentally sent and is not meant for investing in the corresponding strategy, it is still deposited to the relevant Euler's or TrueFi's contract.

## Impact
After the USDC amount that is accidentally sent to the `EulerStrategy` or `TrueFiStrategy` contract is transferred to the relevant Euler's or TrueFi's contract, it cannot be returned to the sender, who accidentally sent it, promptly because it cannot be transferred to `core` immediately. Also, the sender might lose some or all of such amount, which is not designated for investing in the corresponding strategy, if such strategy results in loss of value or requires a fee that is somewhat high.

## Code Snippet
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L51-L55
```solidity
  function _deposit() internal override whenNotPaused {
    // Deposit all current balance into euler
    // https://github.com/euler-xyz/euler-contracts/blob/master/contracts/modules/EToken.sol#L148
    EUSDC.deposit(SUB_ACCOUNT, type(uint256).max);
  }
```

https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L88-L104
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
In each of the `EulerStrategy` and `TrueFiStrategy` contracts, a state variable can be added to bookkeep the USDC amount, which is owned by the contract, that is designated for investing in the corresponding strategy. When calling the `EulerStrategy._deposit` or `TrueFiStrategy._deposit` function, only the designated USDC amount would be deposited to the relevant Euler's or TrueFi's contract.
