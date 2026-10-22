# [H] Possible Precision Issue in LToken::_redeem()

## Summary
Severity: High
Contest weight: 0.6424
Dataset id: 12375
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LayerBank protocol is in essence an over-collateralized lending pool that has the lending functionality and supports a number of normal lending functionalities for supplying and borrowing users, i.e., mint()/redeem() and borrow()/repay(). While reviewing the redeem logic, we notice the current implementation has a precision issue that has been reflected in a recent HundredFinance hack. To elaborate, we show below the related _redeem() routine. As the name indicates, this routine is designed to redeem LToken in exchange for the underlying asset. When the user indicates the underlying asset amount (via redeemUnderlying()), the respective lAmountToRedeem is computed as uAmountIn.mul(1e18).div(exchangeRate()) (line 248). Unfortunately, the current approach may unintentionally introduce a precision issue by computing the lAmountToRedeem amount against the protocol. Specifically, the resulting flooring-based division introduces a precision loss, which may be just a small number but plays a critical role when certain boundary conditions are met as demonstrated in the recent HundredFinance hack: https://blog.hundred.finance/15-04-23-hundred-finance-hack-post-mortem-d895b618cf33.
```solidity
function _redeem(address account, uint256 lAmountIn, uint256 uAmountIn) private returns(uint256) {
    require(lAmountIn == 0 || uAmountIn == 0, "LToken: one of lAmountIn or uAmountIn must be zero");
    require(totalSupply >= lAmountIn, "LToken: not enough total supply");
    require(getCash() >= uAmountIn || uAmountIn == 0, "LToken: not enough underlying");
    require(getCash() >= lAmountIn.mul(exchangeRate()).div(1e18) || lAmountIn == 0, "LToken: not enough underlying");
    uint lAmountToRedeem = lAmountIn > 0 ? lAmountIn : uAmountIn.mul(1e18).div(exchangeRate());
    uint uAmountToRedeem = lAmountIn > 0 ? lAmountIn.mul(exchangeRate()).div(1e18) : uAmountIn;
    require(
        IValidator(core.validator()).redeemAllowed(address(this), account, lAmountToRedeem),
        "LToken: cannot redeem"
    );
    updateSupplyInfo(account, 0, lAmountToRedeem);
    _doTransferOut(account, uAmountToRedeem);
    emit Transfer(account, address(0), lAmountToRedeem);
    emit Redeem(account, uAmountToRedeem, lAmountToRedeem);
    return uAmountToRedeem;
}
```

## Recommendation
Properly revise the above routine to ensure the precision loss needs to be computed in favor of the protocol, instead of the user. In particular, we need to ensure that markets are never empty by minting small LToken balances at the time of market creation so that we can prevent the rounding error being used maliciously. A deposit as small as 1 wei is sufficient.
