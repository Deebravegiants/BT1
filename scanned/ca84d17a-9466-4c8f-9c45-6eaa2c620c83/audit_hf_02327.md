# [M] Revised Withdrawal of ETH in cancelIncreaseOrder()

## Summary
Severity: Medium
Contest weight: 0.4329
Dataset id: 12649
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Perpetual protocol, the FutureRouter contract is a router that facilitates user trading with the Future/FutureLimit contracts. To facilitate user trading by directly using the native token, i.e., ETH, it automatically converts between ETH and WETH. When WETH is to be refunded to the user, it withdraws ETH from WETH and transfers ETH to the user. While reviewing the withdrawal of ETH in the cancelIncreaseOrder() routine, we notice it uses the futureLimit as WETH by mistake.
In the following, we show the code snippet of the FutureRouter::cancelIncreaseOrder() routine, which is used to cancel an existing IncreaseOrder. If the collateral token of the order is WETH, it cancels the order and is expected to withdraw ETH from WETH. However, we notice it calls IWETH(futureLimit).withdraw() (line 304) to withdraw ETH, which will fail. It shall be corrected to call IWETH(weth).withdraw() to withdraw ETH.
```solidity
function cancelIncreaseOrder(uint256 _orderIndex) public {
    (address collateralToken, , , , uint256 _marginDelta, , , ) = IFutureLimit(futureLimit).getIncreaseOrder(msg.sender, _orderIndex);
    if (collateralToken == weth && _marginDelta > 0) {
        IFutureLimit(futureLimit).cancelIncreaseOrder(
            msg.sender,
            _orderIndex,
            address(this),
            payable(msg.sender)
        );
        IWETH(futureLimit).withdraw(_marginDelta);
        _transferOutETH(_marginDelta, payable(msg.sender));
    } else
```

## Recommendation
Revisit the cancelIncreaseOrder() routine and withdraw ETH from WETH.
