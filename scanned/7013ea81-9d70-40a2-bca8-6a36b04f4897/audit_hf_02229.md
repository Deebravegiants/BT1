# [M] Improved buy()/sell() Logic in INTRouterLibrary

## Summary
Severity: Medium
Contest weight: 0.4612
Dataset id: 12309
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The InteNet protocol has a key library named INTRouterLibrary that contains the sell/buy logic for the launched tokens. In the process of examining the related token sell/buy implementation, we notice it can be improved to explicitly indicate the fund source for the associated transaction.
In the following, we show the implementation of the example buy() routine. As the name indicates, this routine is used to buy the new token being launched with the given assetToken.
And the assetToken amount is provided by the calling user, i.e., msg.sender, not the given input argument of to1. With that, we suggest to use msg.sender when transferring the assetToken amount to the pair (line 245) and transferring the buy fee to the treasury (line 247). Note the sell() counterpart routine can be similarly improved.
```solidity
function buy(
    INTFactory factory,
    address assetToken,
    uint256 amountIn,
    address tokenAddress,
    address to
) public returns (uint256, uint256) {
    if (tokenAddress == address(0)) revert TokenIsZeroAddress();
    if (to == address(0)) revert RecipientIsZeroAddress();
    if (amountIn == 0) revert InputAmountIsZero();
    // Fortunately, the current implementation hardcodes the to state with msg.sender. Nevertheless, at least semantically, the funding source is msg.sender, not to.
    address pair = factory.getPair(tokenAddress, assetToken);
    (uint256 amountOut, uint256 txFee) = quoteBuy(
        factory,
        assetToken,
        tokenAddress,
        amountIn
    );
    uint256 amount = amountIn - txFee;
    IERC20(assetToken).safeTransferFrom(to, pair, amount);
    collectFee(factory, assetToken, to, address(0), tokenAddress, txFee);
    IINTPair(pair).transferTo(to, amountOut);
    IINTPair(pair).swap(0, amountOut, amount, 0);
    (uint256 reserveA, uint256 reserveB) = IINTPair(pair).getReserves();
    emit Buy(
        to,
        tokenAddress,
        amountOut,
        amount,
        txFee,
        reserveA,
        reserveB,
        block.timestamp
    );
    return (amountIn, amountOut);
}
```
Moreover, the sell() routine has another issue in updating the pair reserves. In particular, they are currently updated as pair.swap(amountIn, 0, 0, amountOut) (line 206), which should be revised as pair.swap(amountIn, 0, 0, amountOut + txFee)

## Recommendation
Revise the above-mentioned buy()/sell() routines to properly use the funding source for the associated token buy/sell transactions and update the pair reserves.
