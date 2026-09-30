# [M] Unsafe arithmetic casts

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The reason for using signed integers in some situations appears to be to use negative values as an indicator to withdraw everything. Using a whole bit of uint256 for this is quite a lot when using `type(uint256).max` would equal or better serve as a flag to withdraw everything.

Furthermore, even though the code uses `solidity 0.8.x`, which safeguards arithmetic operations against under/overflows, arithmetic typecast is not protected.

Also, see 26 for a related issue.

```console
⇒  solidity-shell

🚀 Entering interactive Solidity ^0.8.11 shell. '.help' and '.exit' are your friends.
 »  ℹ️  ganache-mgr: starting temp. ganache instance ...
 »  uint(int(-100))
115792089237316195423570985008687907853269984665640564039457584007913129639836
 »  int256(uint(2**256-100))
-100
```

#### Examples


**code/contracts/fantom/FliquidatorFTM.sol:L167-L178**
```solidity
// Compute how much collateral needs to be swapt
uint256 collateralInPlay = _getCollateralInPlay(
  vAssets.collateralAsset,
  vAssets.borrowAsset,
  debtTotal + bonus
);

// Burn f1155
_burnMulti(addrs, borrowBals, vAssets, _vault, f1155);

// Withdraw collateral
IVault(_vault).withdrawLiq(int256(collateralInPlay));
```


**code/contracts/fantom/FliquidatorFTM.sol:L264-L276**
```solidity
// Compute how much collateral needs to be swapt for all liquidated users
uint256 collateralInPlay = _getCollateralInPlay(
  vAssets.collateralAsset,
  vAssets.borrowAsset,
  _amount + _flashloanFee + bonus
);

// Burn f1155
_burnMulti(_addrs, _borrowBals, vAssets, _vault, f1155);

// Withdraw collateral
IVault(_vault).withdrawLiq(int256(collateralInPlay));

```


**code/contracts/fantom/FliquidatorFTM.sol:L334-L334**
```solidity
uint256 amount = _amount < 0 ? debtTotal : uint256(_amount);
```


**code/contracts/fantom/FujiVaultFTM.sol:L213-L220**
```solidity
function withdrawLiq(int256 _withdrawAmount) external override nonReentrant onlyFliquidator {
  // Logic used when called by Fliquidator
  _withdraw(uint256(_withdrawAmount), address(activeProvider));
  IERC20Upgradeable(vAssets.collateralAsset).univTransfer(
    payable(msg.sender),
    uint256(_withdrawAmount)
  );
}
```

* pot. unsafe truncation (unlikely)


**code/contracts/FujiERC1155.sol:L53-L59**
```solidity
function updateState(uint256 _assetID, uint256 newBalance) external override onlyPermit {
  uint256 total = totalSupply(_assetID);
  if (newBalance > 0 && total > 0 && newBalance > total) {
    uint256 newIndex = (indexes[_assetID] * newBalance) / total;
    indexes[_assetID] = uint128(newIndex);
  }
}
```

#### Recommendation

If negative values are only used as a flag to indicate that all funds should be used for an operation, use `type(uint256).max` instead. It is wasting less value-space for a simple flag than using the uint256 high-bit range. Avoid typecast where possible. Use `SafeCast` instead or verify that the casts are safe because the values they operate on cannot under- or overflow. Add inline code comments if that's the case.
