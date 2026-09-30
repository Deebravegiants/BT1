# [C] Possible Stealing of Funds From Approving Users

## Summary
Severity: Critical
Contest weight: 0.6075
Dataset id: 13127
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Swing Aggregator protocol has a number of bridge contracts that are provided to seamlessly interact with various cross-chain solutions. In the process of examining these bridge contracts, we notice a need of validating and whitelisting the calling targets so that no user funds will be at risk.

```solidity
function swapExternal(
    IERC20 srcToken,
    DataTypes.SplitSwapInfo memory splitSwapData
) external {
    require(msg.sender == address(this), "Msg.sender can be contract it self");
    if (splitSwapData.spender != address(0) && !srcToken.isETH()) {
        // Manually transfer instead approve
        srcToken.universalTransfer(splitSwapData.swapContract, splitSwapData.amount);
    } else {
        srcToken.universalApprove(splitSwapData.spender, splitSwapData.amount);
    }
    (bool success, ) = splitSwapData.swapContract.call{
        value: srcToken.isETH() ? splitSwapData.amount : 0
    }(splitSwapData.swapData);
    require(success, "External swap failed");
}
```

To elaborate, we show above an example SwapRouter contract and its swapExternal() function. As the name indicates, this function is used to call an example contract given as splitSwapData. swapContract and ensure the call is successful. However, the calling target is not validated, which may be exploited to drain funds from users who have approved funds to this SwapRouter contract. Note this issue aﬀects a number of existing bridge contracts, including SwitchAcross, SwitchCelerSender/Receiver, and others.

## Recommendation
Improve the above logic to ensure the calling targets are whitelisted and properly validated.
