# [H] The withdrawValue calculation in _calculateValueOfWithdrawRequest

## Summary
Severity: High
Contest weight: 0.7844
Dataset id: 22977
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdrawValue calculation in _calculateValueOfWithdrawRequest is incorrect.

```solidity
function _calculateValueOfWithdrawRequest(
  WithdrawRequest memory w,
  uint256 stakeAssetPrice,
  address borrowToken,
  address redeemToken
) internal view returns (uint256 borrowTokenValue) {
  if (w.requestId == 0) return 0;
  // If a withdraw request has split and is finalized, we know the fully realized value of
  // the withdraw request as a share of the total realized value.
  if (w.hasSplit) {
    SplitWithdrawRequest memory s = VaultStorage.getSplitWithdrawRequest()[w.requestId];
    if (s.finalized) {
      return _getValueOfSplitFinalizedWithdrawRequest(w, s, borrowToken, redeemToken);
    }
  }
  // In every other case, including the case when the withdraw request has split, the vault shares
  // in the withdraw request (`w`) are marked at the amount of vault shares the account holds.
  return _getValueOfWithdrawRequest(w, stakeAssetPrice);
}
```

We can see that for cases without hasSplit or with hasSplit but not finalized, the value is calculated using _getValueOfWithdrawRequest. Let’s take a look at PendlePTEtherFiVault::_getValueOfWithdrawRequest().

```solidity
function _getValueOfWithdrawRequest(
  WithdrawRequest memory w, uint256 /* */
) internal override view returns (uint256) {
  uint256 tokenOutSY = getTokenOutSYForWithdrawRequest(w.requestId);
  (int256 weETHPrice, /* */) = TRADING_MODULE.getOraclePrice(TOKEN_OUT_SY, BORROW_TOKEN);
  return (tokenOutSY * weETHPrice.toUint() * BORROW_PRECISION) / (WETH_PRECISION * Constants.EXCHANGE_RATE_PRECISION);
}
```

Here, tokenOutSY represents the total amount of WETH requested for withdrawal, not just the portion represented by the possibly split w.vaultShares. Therefore, _getValueOfWithdrawRequest returns the entire withdrawal value. If a WithdrawRequest has been split but not finalized, this results in an incorrect calculation.

This issue also occurs in PendlePTKelpVault::_getValueOfWithdrawRequest().

```solidity
function _getValueOfWithdrawRequest(
  WithdrawRequest memory w, uint256 /* */
) internal override view returns (uint256) {
  return KelpLib._getValueOfWithdrawRequest(w, BORROW_TOKEN, BORROW_PRECISION);
}
```

//KelpLib._getValueOfWithdrawRequest) function
```solidity
function _getValueOfWithdrawRequest(
  WithdrawRequest memory w,
  address borrowToken,
  uint256 borrowPrecision
) internal view returns (uint256) {
  address holder = address(uint160(w.requestId));
  uint256 expectedStETHAmount;
  if (KelpCooldownHolder(payable(holder)).triggered()) {
    uint256[] memory requestIds = LidoWithdraw.getWithdrawalRequests(holder);
    ILidoWithdraw.WithdrawalRequestStatus[] memory withdrawsStatus = LidoWithdraw.getWithdrawalStatus(requestIds);
    expectedStETHAmount = withdrawsStatus[0].amountOfStETH;
  } else {
    (/* */, expectedStETHAmount, /* */, /* */) = WithdrawManager.getUserWithdrawalRequest(stETH, holder, 0);
  }
  (int256 stETHToBorrowRate, /* */) = Deployments.TRADING_MODULE.getOraclePrice(address(stETH), borrowToken);
  return (expectedStETHAmount * stETHToBorrowRate.toUint() * borrowPrecision) / (Constants.EXCHANGE_RATE_PRECISION * stETH_PRECISION);
}
```

This issue also occurs in PendlePTStakedUSDeVault::_getValueOfWithdrawRequest().

```solidity
function _getValueOfWithdrawRequest(
  WithdrawRequest memory w, uint256 /* */
) internal override view returns (uint256) {
  // so we do not
  // need to use the PendlePT metadata conversion.
  return EthenaLib._getValueOfWithdrawRequest(w, BORROW_TOKEN, BORROW_PRECISION);
}
```

//EthenaLib._getValueOfWithdrawRequest()
```solidity
function _getValueOfWithdrawRequest(
  WithdrawRequest memory w,
  address borrowToken,
  uint256 borrowPrecision
) internal view returns (uint256) {
  address holder = address(uint160(w.requestId));
  // This valuation is the amount of USDe the account will receive at cooldown, once
  // a cooldown is initiated the account is no longer receiving sUSDe yield. This balance
  // of USDe is transferred to a Silo contract and guaranteed to be available once the
  // cooldown has passed.
  IsUSDe.UserCooldown memory userCooldown = sUSDe.cooldowns(holder);
  int256 usdeToBorrowRate;
  if (borrowToken == address(USDe)) {
    usdeToBorrowRate = int256(Constants.EXCHANGE_RATE_PRECISION);
  } else {
    // If not borrowing USDe, convert to the borrowed token
    (usdeToBorrowRate, /* */) = Deployments.TRADING_MODULE.getOraclePrice(address(USDe), borrowToken);
  }
  return (userCooldown.underlyingAmount * usdeToBorrowRate.toUint() * borrowPrecision) / (Constants.EXCHANGE_RATE_PRECISION * USDE_PRECISION);
}
```

The calculation is correct only in EtherFiVault::_getValueOfWithdrawRequest().

```solidity
function _getValueOfWithdrawRequest(
  WithdrawRequest memory w, uint256 weETHPrice
) internal override view returns (uint256) {
  return EtherFiLib._getValueOfWithdrawRequest(w, weETHPrice, BORROW_PRECISION);
}
```

//EtherFiLib._getValueOfWithdrawRequest() function
```solidity
function _getValueOfWithdrawRequest(
  WithdrawRequest memory w,
  uint256 weETHPrice,
  uint256 borrowPrecision
) internal pure returns (uint256) {
  return (w.vaultShares * weETHPrice * borrowPrecision) / (uint256(Constants.INTERNAL_TOKEN_PRECISION) * Constants.EXCHANGE_RATE_PRECISION);
}
```

Overestimation of user assets can lead to scenarios where users should have been liquidated but were not, resulting in losses for the protocol.

## Recommendation
Modify the relevant calculation formulas.
