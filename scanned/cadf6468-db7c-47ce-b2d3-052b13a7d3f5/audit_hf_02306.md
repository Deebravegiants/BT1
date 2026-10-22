# [C] Possible Drained Reserve From exchangeAndStoreTokens()

## Summary
Severity: Critical
Contest weight: 0.6375
Dataset id: 12569
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the token purchase and sale, the Nested protocol has an internal helper routine exchangeAndStoreTokens(). This routine is developed to purchase tokens and store them in a reserve for the user. Note this routine is used in a number of scenarios. In the following, we examine this routine and report related issues in current implementation.
To elaborate, we show below the exchangeAndStoreTokens() implementation. This routine allows the user to provide an arbitrary callData that is used directly in address(reserve).call() (line 211) and ExchangeHelpers.fillQuote() (line 215). Unfortunately, in each case, the arbitrary callData may be exploited to transfer all funds out of the current reserve.
```solidity
function exchangeAndStoreTokens(
    uint256 _nftId,
    IERC20 _sellToken,
    address payable _swapTarget,
    NestedStructs.TokenOrder[] calldata _tokenOrders
) internal {
    uint256 buyCount = _tokenOrders.length;
    for (uint256 i = 0; i < buyCount; i++) {
        uint256 amountBought = 0;
        uint256 balanceBeforePurchase = IERC20(_tokenOrders[i].token).balanceOf(address(this));
        /* If token being exchanged is the sell token, the callData sent by the caller
         ** will be used on the reserve to call the transferFromFactory, taking the funds directly instead swapping
         */
        if (_tokenOrders[i].token == address(_sellToken)) {
            ExchangeHelpers.setMaxAllowance(_sellToken, address(reserve));
            (bool success, ) = address(reserve).call(_tokenOrders[i].callData);
            require(success, "NestedFactory: RESERVE_CALL_FAILED");
            amountBought = balanceBeforePurchase - IERC20(_tokenOrders[i].token).balanceOf(address(this));
        } else {
            bool success = ExchangeHelpers.fillQuote(_sellToken, _swapTarget, _tokenOrders[i].callData);
            require(success, "NestedFactory: SWAP_CALL_FAILED");
            amountBought = IERC20(_tokenOrders[i].token).balanceOf(address(this)) - balanceBeforePurchase;
            IERC20(_tokenOrders[i].token).safeTransfer(address(reserve), amountBought);
        }
        nestedRecords.store(_nftId, _tokenOrders[i].token, amountBought, address(reserve));
    }
}
```
In particular, using the ﬁrst case as an example. If the callData is encoded to call reserve's function transfer(_recipient, _token, _amount) where the _amount = _token.balanceOf(reserve). In other words, all _token funds available in the reserve may be withdrawn by the current user.

## Recommendation
Apply necessary rigorous validity checks on untrusted user input so that the user is only allowed to access the user's funds in the reserve, not others.
