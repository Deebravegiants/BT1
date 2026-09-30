# [M] Proper Refund of The Excess BNB

## Summary
Severity: Medium
Contest weight: 0.4593
Dataset id: 11928
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Crossroad.gold, there is a handy contract LiquidityProxy which provides a number of convenience routines for liquidation addition/removal, e.g., addLiquidity(), addLiquidityBnb(), removeLiquidity(), and removeLiquidityBnb(). During the analysis of these convenience routines, we notice that addLiquidityBnb() does not refund the excess BNB properly.
To elaborate, we show below the implementation of addLiquidityBnb(). This routine receives BNB and tokens from the caller, provides them to the _tokenLp pool as liquidity, and then refunds the excess BNB to the caller. Typically, the excess BNB is calculated by subtracting the amount of BNB consumed in the liquidity addition from the amount of BNB received from the caller.
```solidity
function addLiquidityBnb(
    address _factory,
    address _tokenLp,
    address _token,
    uint _amountTokenDesired,
    uint _amountBnbDesired,
    uint _amountTokenMin,
    uint _amountBnbMin,
    address _to
) external payable returns (uint amountToken_, uint amountBnb_, uint liquidity_) {
    require(_amountBnbDesired <= msg.value, "LiquidityProxy: Insufficient BNB");
    factoryEnsurePairExistsInner(_factory, _token, WBNB);
    (amountToken_, amountBnb_) = getAddLiquidityAmountsInner(
        _tokenLp,
        _token,
        WBNB,
        _amountTokenDesired,
        _amountBnbDesired,
        _amountTokenMin,
        _amountBnbMin
    );
    IERC20(_token).safeTransferFrom(msg.sender, _tokenLp, amountToken_);
    IWETH(WBNB).deposit{value: amountBnb_}();
    IERC20(WBNB).safeTransfer(_tokenLp, amountBnb_);
    liquidity_ = IUniswapPool(_tokenLp).mint(_to);
    // refund excess bnb
    if (_amountBnbDesired > amountBnb_) TransferHelper.safeTransferETH(msg.sender, _amountBnbDesired - amountBnb_);
}
```
However, it comes to our attention that the current implementation, amountBnbDesired - amountBnb_ (line 114), is subtracting the amount of BNB consumed in the liquidity addition from the amount of BNB desired by the caller. This will cause msg.value - _amountBnbDesired amount of BNB left in the contract.

## Recommendation
Calculate the excess BNB by subtracting amountBnb_ from msg.value.
