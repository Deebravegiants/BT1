# [M] Lack of Slippage Control In Switch

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 13142
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The swapByNxtp() function of the SwitchNxtp contract can support the swap from srcSwap.srcToken to srcSwap.dstToken before bridging via the Nxtp. While examining the implementation logic of this routine, we observe that there is no slippage control in place, which opens up the possibility for front-running and potentially results in a smaller returnAmount (line 131). Moreover, a similar issue also exists in the SwitchStargateSender, SwitchStargateReceiver, and SwitchCelerReceiver contracts.
```solidity
function swapByNxtp(
    SwapArgsNxtp calldata transferArgs,
    bytes calldata encryptedCallData,
    bytes calldata encodedBid,
    bytes calldata bidSignature
) external payable nonReentrant returns (ITransactionManager.TransactionData memory) {
    require(transferArgs.recipient == msg.sender, "recipient must be equal to caller");
    require(transferArgs.invariantData.receivingAddress == msg.sender, "recipient must be equal to caller");
    require(transferArgs.expectedReturn >= transferArgs.minReturn, "expectedReturn must be equal or larger than minReturn");
    IERC20(transferArgs.srcSwap.srcToken).universalTransferFrom(msg.sender, address(this), transferArgs.amount);
    uint256 returnAmount = 0;
    uint256 amountAfterFee = _getAmountAfterFee(
        IERC20(transferArgs.srcSwap.srcToken),
        transferArgs.amount,
        transferArgs.partner,
        transferArgs.partnerFeeRate
    );
    // check fromToken is same or not destToken
    if (transferArgs.srcSwap.srcToken == transferArgs.srcSwap.dstToken)
        returnAmount = amountAfterFee;
    else
        returnAmount = _swapBeforeNxtp(transferArgs, amountAfterFee);
    if (returnAmount > 0) {
        uint256 approvedAmount = IERC20(transferArgs.srcSwap.dstToken).allowance(address(this), transactionManagerAddress);
        if (approvedAmount < returnAmount)
            IERC20(transferArgs.srcSwap.dstToken).safeIncreaseAllowance(transactionManagerAddress, returnAmount);
        _emitCrossChainSwapRequest(transferArgs, returnAmount, msg.sender);
        return transactionManager.prepare(ITransactionManager.PrepareArgs({
            invariantData: transferArgs.invariantData,
            amount: returnAmount,
            expiry: transferArgs.expiry,
            encryptedCallData: encryptedCallData,
            encodedBid: encodedBid,
            bidSignature: bidSignature,
            encodedMeta: "Ox"
        }));
    } else {
        IERC20(transferArgs.srcSwap.srcToken).universalTransferFrom(address(this), msg.sender, transferArgs.amount);
        revert("Swap failed from dex");
    }
}
```
Note that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the liquidity provider. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Develop an effective mitigation to the above sandwich arbitrage to better protect the interests of users.
