# [M] If admin of USDC blocks the relevant Euler's or TrueFi's contract from sending USDC, then the Euler or TrueFi strategy cannot be removed or replaced

## Summary
Severity: Medium
Reporter: rbserver
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L45-L47
Type: audit-issue

## Details
# If admin of USDC blocks the relevant Euler's or TrueFi's contract from sending USDC, then the Euler or TrueFi strategy cannot be removed or replaced

## Summary
The Euler or TrueFi strategy cannot be removed or replaced if the admin of USDC adds the relevant Euler's or TrueFi's contract address on USDC's blocklist.

## Vulnerability Detail
After the `EulerStrategy` or `TrueFiStrategy` contract's USDC balance is transferred to the corresponding Euler or TrueFi's contract, the `EulerStrategy._balanceOf` or `TrueFiStrategy._balanceOf` function, as shown in the Code Snippet section, would return a positive value. Since USDC includes a blocklist, there is no guarantee that the admin of USDC will not block the relevant Euler's or TrueFi's contract from sending USDC in the future. If this happens before the `EulerStrategy` or `TrueFiStrategy` contract withdraws all relevant USDC amount from the corresponding Euler's or TrueFi's contract, then `EulerStrategy._balanceOf` or `TrueFiStrategy._balanceOf` would never return 0. In this situation, calling the `BaseStrategy.remove` or `BaseStrategy.replace` function would always revert because of `if (_balanceOf() != 0) revert NonZeroBalance()`.

## Impact
For the described scenario, since calling `BaseStrategy.remove` or `BaseStrategy.replace` would always revert, the Euler or TrueFi strategy cannot be removed or replaced anymore.

## Code Snippet
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/EulerStrategy.sol#L45-L47
```solidity
  function _balanceOf() internal view override returns (uint256) {
    return EUSDC.balanceOfUnderlying(address(this));
  }
```

https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L134-L147
```solidity
  function _balanceOf() internal view override returns (uint256) {
    // https://docs.truefi.io/faq/main-lending-pools/developer-guide/truefipool2-contract#calculating-lending-pool-token-prices

    // How much USDC is locked in TrueFi
    // Based on staked tfUSDC + tfUSDC in this contract
    uint256 tfUsdcBalance = (tfUSDC.poolValue() *
      (_viewTfUsdcStaked() + tfUSDC.balanceOf(address(this)))) / tfUSDC.totalSupply();

    // How much USDC we get if we liquidate the full position
    tfUsdcBalance = (tfUsdcBalance * tfUSDC.liquidExitPenalty(tfUsdcBalance)) / BASIS_PRECISION;

    // Return USDC in contract + USDC we can get from TrueFi
    return want.balanceOf(address(this)) + tfUsdcBalance;
  }
```

https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/base/BaseStrategy.sol#L37-L47
```solidity
  function remove() external virtual override onlyOwner {
    _withdrawAll();
    if (_balanceOf() != 0) revert NonZeroBalance();
    parent.childRemoved();
  }

  function replace(INode _newNode) external virtual override onlyOwner {
    _withdrawAll();
    if (_balanceOf() != 0) revert NonZeroBalance();
    _replace(_newNode);
  }
```


## Tool used

Manual Review

## Recommendation
The `BaseStrategy.remove` and `BaseStrategy.replace` functions can be updated to check if the corresponding Euler's and TrueFi's contracts are on USDC's blocklist or not; these functions could only execute `if (_balanceOf() != 0) revert NonZeroBalance()` if such contracts are not on the blocklist at that moment.
