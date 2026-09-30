# [M] Potential Sandwich/MEV Attack For createOption()

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 12211
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Facade contract, the createOption() function is designed to allow buyers to purchase the put/call options. Our analysis shows there is a potential Sandwich/MEV attack for the createOption() function. To elaborate, we show below the related code snippet of the contract. In the createOption() function, if the payment token of the buyer is not the underlying token of the Hegic Pool, the swapTokensForExactTokens() function (line 152) of UniswapV2 will be called to swap the payment token of the buyer to the underlying token of the Hegic Pool. We notice the optionPrice is calculated by the exchange.getAmountsIn(_baseTotal, swappath)[0] (line 82), which is the actual amount of the payment token that will be swapped. However, it is assigned to the amountInMax of the swapTokensForExactTokens() function, which means the restriction on possible slippage will never take effect and is therefore vulnerable to possible front-running attacks.
```solidity
function createOption(
    IHegicPool pool,
    uint256 period,
    uint256 amount,
    uint256 strike,
    address[] calldata swappath
) external payable {
    address buyer = _msgSender();
    (uint256 optionPrice, uint256 rawOptionPrice,,) =
    getOptionPrice(pool, period, amount, strike, swappath);
    IERC20 paymentToken = IERC20(swappath[0]);
    paymentToken.safeTransferFrom(buyer, address(this), optionPrice);
    if (swappath.length > 1) {
        if (paymentToken.allowance(address(this), address(exchange)) < optionPrice)
            paymentToken.approve(address(exchange), type(uint256).max);
        exchange.swapTokensForExactTokens(
            rawOptionPrice,
            optionPrice,
            swappath,
            address(this),
            block.timestamp
        );
    }
    pool.sellOption(buyer, period, amount, strike);
}

function getOptionPrice(
    IHegicPool pool,
    uint256 period,
    uint256 amount,
    uint256 strike,
    address[] calldata swappath
) public view returns (
    uint256 total,
    uint256 baseTotal,
    uint256 settlementFee,
    uint256 premium
) {
    (uint256 _baseTotal, uint256 baseSettlementFee, uint256 basePremium) =
    getBaseOptionCost(pool, period, amount, strike);
    if (swappath.length > 1)
        total = exchange.getAmountsIn(_baseTotal, swappath)[0];
    else
        total = _baseTotal;
    baseTotal = _baseTotal;
    settlementFee = (total * baseSettlementFee) / baseTotal;
    premium = (total * basePremium) / baseTotal;
```

## Recommendation
Improve the createOption() function by adding necessary slippage control.
