# [M] D3VaultFunding.userWithdraw() does not have minTokenAmount

## Summary
Severity: Medium
Contest weight: 0.5847
Dataset id: 20089
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
D3VaultFunding.userWithdraw() does not have minTokenAmount, and use _getExchangeRate directly. This is vulnerable to a sandwich attack.
As we can see, D3VaultFunding.userWithdraw() does not have minTokenAmount, and use _getExchangeRate directly.
```solidity
function userWithdraw(address to, address user, address token, uint256 dTokenAmount) external nonReentrant allowedToken(token) returns(uint256 amount) {
    accrueInterest(token);
    AssetInfo storage info = assetInfo[token];
    require(dTokenAmount <= IDToken(info.dToken).balanceOf(msg.sender), Errors.DTOKEN_BALANCE_NOT_ENOUGH);
    // check amount value
    IDToken(info.dToken).burn(msg.sender, dTokenAmount);
    IERC20(token).safeTransfer(to, amount);
    info.balance = info.balance - amount;
    // used for calculate user withdraw amount
    // this function could be called from d3Proxy, so we need "user" param
    // In the meantime, some users may hope to use this function directly,
    // to prevent these users fill "user" param with wrong addresses,
    // we use "msg.sender" param to check.
    emit UserWithdraw(msg.sender, user, token, amount);
}
```
And the _getExchangeRate() result is about cash, info.totalBorrows, info.totalReserves, info.withdrawnReserves, dTokenSupply. This is vulnerable to a sandwich attack leading to huge slippage
```solidity
function _getExchangeRate(address token) internal view returns (uint256) {
    AssetInfo storage info = assetInfo[token];
    uint256 cash = getCash(token);
    uint256 dTokenSupply = IERC20(info.dToken).totalSupply();
    if (dTokenSupply == 0) { return 1e18; }
    return (cash + info.totalBorrows - (info.totalReserves - info.withdrawnReserves)).div(dTokenSupply);
}
```
This is vulnerable to a sandwich attack.

## Recommendation
Add minTokenAmount parameter for userWithdraw() function and check if amount < minTokenAmount
