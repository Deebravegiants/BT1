# [M] Loss of precision leads to undercollateralized

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-pooltogether
Published: 2023-07-12
Source: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/143
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/b1deb5d494c25f885c34c83f014c8a855c5e2749/src/Vault.sol#L1176


# Vulnerability details

## Impact
Since `_yieldVault` mostly calculates `shares` use `round down` when depositing, there is often a `1 wei` loss of precision, which can cause the `vault` to go into `undercollateralized` mode by mistake.

## Proof of Concept
When a user deposits an asset, we update `_lastRecordedExchangeRate`, the calculation is done by this method `_currentExchangeRate()`

The code is as follows:

```solidity
  function _currentExchangeRate() internal view returns (uint256) {
    uint256 _totalSupplyAmount = _totalSupply();
    uint256 _totalSupplyToAssets = _convertToAssets(
      _totalSupplyAmount,
      _lastRecordedExchangeRate,
      Math.Rounding.Down
    );

@>  uint256 _withdrawableAssets = _yieldVault.maxWithdraw(address(this));

    if (_withdrawableAssets > _totalSupplyToAssets) {
      _withdrawableAssets = _withdrawableAssets - (_withdrawableAssets - _totalSupplyToAssets);
    }

    if (_totalSupplyAmount != 0 && _withdrawableAssets != 0) {
      return _withdrawableAssets.mulDiv(_assetUnit, _totalSupplyAmount, Math.Rounding.Down);
    }

    return _assetUnit;
  }
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-pooltogether-findings/issues/143_
