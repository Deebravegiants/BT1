# [M] Revised Selection of bestRouter in HopeSwapBurner::burn()

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 12277
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LightDAO governance protocol, the HopeSwapBurner contract is designed to convert the received fees to HOPE. It has a list of candidate routers which can be used to complete the swap. In order to receive the most HOPE from the swap, it makes queries to current routers and selects the best one to complete the swap. While reviewing the selection of the best router, we notice it does not use the correct return value from the query. To elaborate, we show below the code snippet of the HopeSwapBurner::burn() routine, which is designed to convert the given fee token, i.e., token, to HOPE. It asks queries for the swap from each of the candidate routers and selects the best one which can offer the most HOPE. The query is carried out by calling the getAmountsOut() routine of each router (line 66), which returns an array of amounts, i.e., expected. The expected array records the amount of the target token it can receive from each step of the swap path. Specially, the first element in the array (expected[0]) is the input token amount, i.e., spendAmount, and the last element in the array (expected[1]) is the amount of the target token, i.e., HOPE. Based on this, it shall use the expected[1] as the query result to choose the best router, not the expected[0] (line 67).

```solidity
function burn(address to, IERC20 token, uint amount, uint amountOutMin) external {
    require(msg.sender == feeVault, "LSB04");
    if (token == HOPE) {
        require(token.transferFrom(msg.sender, to, amount), "LSB00");
        return;
    }
    uint256 balanceBefore = token.balanceOf(address(this));
    require(token.transferFrom(msg.sender, address(this), amount), "LSB01");
    uint256 balanceAfter = token.balanceOf(address(this));
    uint256 spendAmount = balanceAfter - balanceBefore;
    ISwapRouter bestRouter = routers[0];
    uint bestExpected = 0;
    address[] memory path = new address[](2);
    path[0] = address(token);
    path[1] = address(HOPE);
    for (uint i = 0; i < routers.length; i++) {
        uint[] memory expected = routers[i].getAmountsOut(spendAmount, path);
        if (expected[0] > bestExpected) {
            bestExpected = expected[0];
            bestRouter = routers[i];
        }
    }
    require(bestExpected >= amountOutMin, "LSB02");
    if (!approved[bestRouter][token]) { ... }
    bestRouter.swapExactTokensForTokens(spendAmount, 0, path, to, block.timestamp);
}
```

Note the same issue is also applicable to the UnderlyingBurner::burn() routine.

## Recommendation
Revise the above mentioned burn() routine and use expected[1] as the query result to select the best router.
