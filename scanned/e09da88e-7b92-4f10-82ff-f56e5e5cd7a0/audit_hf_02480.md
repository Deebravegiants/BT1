# [C] Possible Fund Stealing From Approving Users

## Summary
Severity: Critical
Contest weight: 0.6325
Dataset id: 13264
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the token swap from Ethereum to THORChain, the TSAggregatorGeneric protocol has a helper routine swapIn(). This routine is developed to transfer user funds into this contract, next use an external router to swap the funds to ETH, and then use the THORChain router to deposit the ETH with a memo with the information about the THORChain asset and the recipient we want to swap to. To elaborate, we show below the swapIn() routine implementation. This routine allows the user to provide an arbitrary router and callData that is used directly in router.call(data) (line 29). However, the arbitrary router and callData may be exploited to transfer all funds from the users to the hacker.

```solidity
function swapIn(
    address tcRouter,
    address tcVault,
    string calldata tcMemo,
    address token,
    uint amount,
    address router,
    bytes calldata data,
    uint deadline
) public nonReentrant {
    token.safeTransferFrom(msg.sender, address(this), amount);
    token.safeApprove(address(router), amount);
    (bool success,) = router.call(data);
    require(success, "failed to swap");
    uint256 amountOut = address(this).balance;
    amountOut = skimFee(amountOut);
    IThorchainRouter(tcRouter).depositWithExpiry{value: amountOut}(
        payable(tcVault),
        address(0), // ETH
        amountOut,
        tcMemo,
        deadline
    );
}
```

Specifically, users usually need to give allowance to the TSAggregatorGeneric contract to facilitate the token swap. To save gas fee, sometimes the user may give a maximum allowance as type(uint256).max to the TSAggregatorGeneric contract! In this case, if the router value is changed to the token address and the callData is encoded to call function token.transferFrom(userAddress, hackerAddress, amount) where the amount = token.balanceOf(userAddress), all token of the user may be withdrawn by the malicious actor.

## Recommendation
Apply necessary rigorous validity checks on the untrusted user input. Also raise the community awareness of not giving token allowance to the TSAggregatorGeneric contract.
