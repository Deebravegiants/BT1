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

This method takes `_yieldVault.maxWithdraw(address(this))` as the maximum value to calculate the current exchange rate.

If the exchange rate is lower than `_assetUnit`, then it goes into `undercollateralized` mode, where it can only be withdraw, not deposit.

So if `_yieldVault` is losing money, it goes into `undercollateralized`.

But there is one missing consideration here: As long as `_yieldVault` is not exclusive, there will be precision loss issues, after `_yieldVault.deposit()`, `maxWithdraw()` will lose precision, because most vaults will do `rounds down` shares calculations
For example: depositing `1000000000`, but it can only withdraw `999999999`.

This leads to the problem that when the first deposit is made, it is likely to go into `undercollateralized` mode immediately due to the `1 wei` loss.

The following code demonstrates that when a non-exclusive `_yieldVault`, `alice` is first deposited normally, it immediately enters `undercollateralized` mode.

add to Deposit.t.sol

```solidity
  function testLossPrecision() external {
    vm.startPrank(alice);
    
    //0.Constructing a yieldVault that is already profitable
    uint256 _amount = 333e18;
    underlyingAsset.mint(alice, _amount);
    underlyingAsset.approve(address(yieldVault), type(uint256).max);   
    yieldVault.deposit(_amount,alice);
    //profitable 0.1e18
    underlyingAsset.mint(address(yieldVault), 0.1e18);

    //1.alice deposit
    _amount = 100e18;
    underlyingAsset.mint(alice, _amount);
    underlyingAsset.approve(address(vault), type(uint256).max);
    console2.log("deposit:",_amount);    
    vault.deposit(_amount, alice);
    console2.log("maxWithdraw:",yieldVault.maxWithdraw(address(vault)));
    console2.log("loss :",_amount - yieldVault.maxWithdraw(address(vault)));
    console2.log("isVaultCollateralized:",vault.isVaultCollateralized());  
    return;
   }
```

```console
$ forge test --match-test testLossPrecision -vvv

[PASS] testLossPrecision() (gas: 402881)
Logs:
  deposit: 100000000000000000000
  maxWithdraw: 99999999999999999999
  loss : 1
  isVaultCollateralized: false

```


This small loss of precision should not be treated as a loss, and we can avoid it by adding `1wei` when calculation exchange rate.

## Tools Used

## Recommended Mitigation Steps


`_yieldVault.maxWithdraw() + 1` Avoid loss of precision into `undercollateralized`


```solidity
  function _currentExchangeRate() internal view returns (uint256) {
    uint256 _totalSupplyAmount = _totalSupply();
    uint256 _totalSupplyToAssets = _convertToAssets(
      _totalSupplyAmount,
      _lastRecordedExchangeRate,
      Math.Rounding.Down
    );

-   uint256 _withdrawableAssets = _yieldVault.maxWithdraw(address(this));
+   uint256 _withdrawableAssets = _yieldVault.maxWithdraw(address(this)) + 1;

    if (_withdrawableAssets > _totalSupplyToAssets) {
      _withdrawableAssets = _withdrawableAssets - (_withdrawableAssets - _totalSupplyToAssets);
    }

    if (_totalSupplyAmount != 0 && _withdrawableAssets != 0) {
      return _withdrawableAssets.mulDiv(_assetUnit, _totalSupplyAmount, Math.Rounding.Down);
    }

    return _assetUnit;
  }
```


## Assessed type

Decimal
