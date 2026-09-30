# [H] Residual ETH not sent back when batchBalanceAndTradeA

## Summary
Severity: High
Contest weight: 0.7870
Dataset id: 22407
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Residual ETH was not sent back when batchBalanceAndTradeAction function was executed, resulting in a loss of assets. At Line 109, it is often the case to have an excess amount to be refunded to the users. 
File: wfCashLogic.sol
094:
```solidity
function _lendLegacy(
```
File: wfCashLogic.sol
109:
```solidity
// If deposit amount external is in excess of the cost to purchase fCash amount (often the case),
// then we need to return the difference between postTradeCash - preTradeCash. This is done because
// the encoded trade does not automatically withdraw the entire cash balance in case the wrapper
// is holding a cash balance.
uint256 preTradeCash = getCashBalance();

BalanceActionWithTrades[] memory action = EncodeDecode.encodeLegacyLendTrade(
    currencyId,
    getMarketIndex(),
    depositAmountExternal,
    fCashAmount,
    minImpliedRate
);
// Notional will return any residual ETH as the native token. When we _sendTokensToReceiver those
// native ETH tokens will be wrapped back to WETH.
NotionalV2.batchBalanceAndTradeAction{value: msgValue}(address(this), action);

uint256 postTradeCash = getCashBalance();

if (preTradeCash != postTradeCash) {
    // If ETH, then redeem to WETH (redeemToUnderlying == false)
    NotionalV2.withdraw(currencyId, _safeUint88(postTradeCash - preTradeCash), !isETH);
}
```
This is due to how the depositUnderlyingExternal function within Notional V3 is implemented. Within the depositUnderlyingExternal function at Line 196, excess ETH will be transferred back to the account (wrapper address) in Native ETH term. But in this case, the wrapper converts the ETH to WETH and adds it to the wrapper's cash balance, and this issue will not occur.
File: TokenHandler.sol
181:
```solidity
function depositUnderlyingExternal(
    address account,
    uint16 currencyId,
    int256 _underlyingExternalDeposit,
    PrimeRate memory primeRate,
    bool returnNativeTokenWrapped
) internal returns (int256 actualTransferExternal, int256 netPrimeSupplyChange) {
    uint256 underlyingExternalDeposit = _underlyingExternalDeposit.toUint();
    if (underlyingExternalDeposit == 0) return (0, 0);

    Token memory underlying = getUnderlyingToken(currencyId);
    if (underlying.tokenType == TokenType.Ether) {
        // Underflow checked above
        if (underlyingExternalDeposit < msg.value) {
            // Transfer any excess ETH back to the account
            GenericToken.transferNativeTokenOut(
                account, msg.value - underlyingExternalDeposit, returnNativeTokenWrapped
            );
        } else {
            require(underlyingExternalDeposit == msg.value, "ETH Balance");
        }
    }

    actualTransferExternal = _underlyingExternalDeposit;
```
But here, residual ETH is returned to the wrapper in native ETH, then when we _sendTokensToReceiver those native ETH tokens will be wrapped back to WETH.
File: wfCashLogic.sol
094:
```solidity
function _lendLegacy(
..SNIP..
122:
// Notional will return any residual ETH as the native token. When we _sendTokensToReceiver those
// native ETH tokens will be wrapped back to WETH.
```
However, the current implementation of the _sendTokensToReceiver, as shown below, does not wrap the Native ETH to WETH. Thus, the residual ETH will not be sent back to the users and stuck in the contract.
File: wfCashLogic.sol
331:
```solidity
function _sendTokensToReceiver(
    IERC20 token,
    address receiver,
    bool isETH,
    uint256 balanceBefore
) private returns (uint256 tokensTransferred) {
    uint256 balanceAfter = isETH ? WETH.balanceOf(address(this)) : token.balanceOf(address(this));
    tokensTransferred = balanceAfter - balanceBefore;

    if (isETH) {
        // No need to use safeTransfer for WETH since it is known to be compatible
        IERC20(address(WETH)).transfer(receiver, tokensTransferred);
    } else if (tokensTransferred > 0) {
        token.safeTransfer(receiver, tokensTransferred);
    }
}
```
Loss of assets as the residual ETH is not sent to the users.

## Recommendation
If the underlying is ETH, measure the Native ETH balance before and after the batchBalanceAndTradeAction is executed. Forward any residual Native ETH to the users, if any.
