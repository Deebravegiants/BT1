# [M] Wrong `lastBuyBackPrice`

## Summary
Severity: Medium
Contest weight: 0.1949
Dataset id: 1386
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `sYETIToken.lastBuyBackPrice` is set in `buyBack` and hardcoded as:
    
    function buyBack(address routerAddress, uint256 YUSDToSell, uint256 YETIOutMin, address[] memory path) external onlyOwner {
        require(YUSDToSell > 0, "Zero amount");
        require(lastBuybackTime + 69 hours < block.timestamp, "Must have 69 hours pass before another buyBack");
        yusdToken.approve(routerAddress, YUSDToSell);
        uint256[] memory amounts = IRouter(routerAddress).swapExactTokensForTokens(YUSDToSell, YETIOutMin, path, address(this), block.timestamp + 5 minutes);
        lastBuybackTime = block.timestamp;
        // amounts[0] is the amount of YUSD that was sold, and amounts[1] is the amount of YETI that was gained in return. So the price is amounts[0] / amounts[1]
        // @audit this hardcoded lastBuybackPrice is wrong when using a different path (think path length 3)
        lastBuybackPrice = div(amounts[0].mul(1e18), amounts[1]);
        emit BuyBackExecuted(YUSDToSell, amounts[0], amounts[1]);
    }

It divides the first and second return `amounts` of the swap, however, these amounts depend on the swap `path` parameter that is used by the caller. If a swap path of length 3 is used, then this is obviously wrong. It also assumes that each router sorts the pairs the same way (which is true for Uniswap/Sushiswap).

## Recommendation
Verify the first and last element of the path are YETI/YUSD and use the first and last amount parameter.

The idea was that on launch we will likely use a curve pool to route through so this contract would change slightly. However it is valid and some more checks would be good to add. Moving to level 1 issue.

A medium severity rating is warranted.
