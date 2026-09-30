# [M] The protocol does not compatible with token

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 20064
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol does not compatible with token such as USDT because of the Approval Race Protection
the protocol is intended to interact with any ERC20 token and USDT is a common one
Q: Which ERC20 tokens do you expect will interact with the smart contracts? The protocol expects to interact with any ERC20.
Individual SetToken's should only interact with ERC20 chosen by the SetToken manager.
when doing the deleverage
https://github.com/IndexCoop/index-protocol/blob/86be7ee76d9a7e4f7e93acfc533216ebef791c89/contracts/protocol/modules/v1/AaveV3LeverageModule.sol#L31
first, we construct the deleverInfo
```solidity
ActionInfo memory deleverInfo = _createAndValidateActionInfo(
    _setToken,
    _collateralAsset,
    _repayAsset,
    _redeemQuantityUnits,
    _minRepayQuantityUnits,
    _tradeAdapterName,
    false
);
```
then we withdraw from the lending pool, execute trade and repay the borrow token
```solidity
_withdraw(deleverInfo.setToken, deleverInfo.lendingPool, _collateralAsset, deleverInfo.notionalSendQuantity);

uint256 postTradeReceiveQuantity = _executeTrade(deleverInfo, _collateralAsset, _repayAsset, _tradeData);

uint256 protocolFee = _accrueProtocolFee(_setToken, _repayAsset, postTradeReceiveQuantity);

uint256 repayQuantity = postTradeReceiveQuantity.sub(protocolFee);
_repayBorrow(deleverInfo.setToken, deleverInfo.lendingPool, _repayAsset, repayQuantity);
```
this is calling _repayBorrow
```solidity
/**
 * @dev Invoke repay from SetToken using AaveV2 library. Burns DebtTokens for SetToken.
 */
function _repayBorrow(ISetToken _setToken, ILendingPool _lendingPool, IERC20 _asset, uint256 _notionalQuantity) internal {
    _setToken.invokeApprove(address(_asset), address(_lendingPool), _notionalQuantity);

    _setToken.invokeRepay(_lendingPool, address(_asset), _notionalQuantity, BORROW_RATE_MODE);
}
```
the trade received (quantity - the protocol fee) is used to repay the debt
but the required debt to be repaid is the (borrowed amount + the interest rate)
suppose the only debt that needs to be repaid is 1000 USDT
trade received (quantity - the protocol fee) is 20000 USDT
only 1000 USDT is used to repay the debt
because when repaying, the paybackAmount is only the debt amount
https://github.com/aave/aave-v3-core/blob/29ff9b9f89af7cd8255231bc5faf26c3ce0fb7ce/contracts/protocol/libraries/logic/BorrowLogic.sol#L204
```solidity
uint256 paybackAmount = params.interestRateMode == DataTypes.InterestRateMode.STABLE
    ? stableDebt
    : variableDebt;
```
then when burning the variable debt token
https://github.com/aave/aave-v3-core/blob/29ff9b9f89af7cd8255231bc5faf26c3ce0fb7ce/contracts/protocol/libraries/logic/BorrowLogic.sol#L224
```solidity
reserveCache.nextScaledVariableDebt = IVariableDebtToken(
    reserveCache.variableDebtTokenAddress
).burn(params.onBehalfOf, paybackAmount, reserveCache.nextVariableBorrowIndex);
```
only the "payback amount", which is 1000 USDT is transferred to pay the debt, the excessive leftover amount is (20000 USDT - 1000 USDT) = 19000 USDT
but if we look back into the repayBorrow function
```solidity
/**
 * @dev Invoke repay from SetToken using AaveV2 library. Burns DebtTokens for SetToken.
 */
function _repayBorrow(ISetToken _setToken, ILendingPool _lendingPool, IERC20 _asset, uint256 _notionalQuantity) internal {
    _setToken.invokeApprove(address(_asset), address(_lendingPool), _notionalQuantity);

    _setToken.invokeRepay(_lendingPool, address(_asset), _notionalQuantity, BORROW_RATE_MODE);
}
```
the approved amount is 20000 USDT, but only 1000 USDT approval limit is used, we have 19000 USDT approval limit left
according to
https://github.com/d-xo/weird-erc20#approval-race-protections
Some tokens (e.g. OpenZeppelin) will revert if trying to approve the zero address to spend tokens (i.e. a call to approve(address(0), amt)).
Integrators may need to add special cases to this logic if working with such a token.
USDT is such token that subject to approval race condition, without approving 0 first, the second approve after first repay will revert
second and following repay borrow will revert if the ERC20 token is subject to approval race condition

## Recommendation
Approval 0 first
