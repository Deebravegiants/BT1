# [M] Gas fee is charged too early and make sponsor lose fund when trigger setupAndTrade if there are bridging transaction

## Summary
Severity: Medium
Contest weight: 0.4596
Dataset id: 22822
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Gas fee is charged too early and make sponsor lose fund when trigger setupAndTrade if there are bridging transaction. In Messi contract, the code to charge gas is: // We charge for gas and fees if (!gasCharged) { (gasCharged, gasAmountCharged) = tryToChargeForGas( (initialGas - gasleft()) * tx.gasprice + valueToSend, gasToFeeTokenExchangeRate, feesTokenAddress, receivingUser, true, gasCharged, // If there is a bridge, we check if the input of the bridge is the fee token // Otherwise, we check if the output of the last swapOp is the fee token // Because if so, we dont need to bring the tokens to the contract bridgeFound? bridgeOp.inputToken != feesTokenAddress: swapOps.length > 0? swapOps[swapOps.length - 1].outputToken != feesTokenAddress: claimOp.outputToken != feesTokenAddress ); } require(gasCharged, "Messi: gas not charged"); as we can see, the gas fee is charged as : (initialGas - gasleft()) * tx.gasprice operation
```solidity
function takeTokensAndTrade(
    OperationParameters[] memory ops,
    uint256 feeRateBps,
    address receivingUser,
    address feesTokenAddress, // always going to be either first or last token in the path
    uint256 gasToFeeTokenExchangeRate
) public payable override noReentrancy onlySponsor notPaused{
    uint256 prevSwapEthBalance = address(this).balance;
    require(msg.sender == sponsor, "Messi: only sponsor can talk to messi");
    require(gasToFeeTokenExchangeRate > 0, "Messi: gasToFeeTokenExchangeRate must be greater than 0");
    require(receivingUser != address(0), "Messi: receivingUser must not be 0x0");
    require(ops.length > 0, "Messi: no operations to execute");
    if (!validateFeeToken(feesTokenAddress, ops)) {
        revert("Messi: fee token must be either input or output token");
    }
    // Separate the claim and bridge operations from the masterProxy operations
    OperationParameters memory claimOp;
    bool claimFound;
    OperationParameters[] memory swapOps;
    OperationParameters memory bridgeOp;
    bool bridgeFound;
    (claimOp, claimFound, swapOps, bridgeOp, bridgeFound) = processOperations(ops);
    bool inputFeeCharged = false;
    bool feesCharged = false;
    bool gasCharged = false;
    uint256 gasAmountCharged = 0;
    // We start considering the gas from this point forward
    uint256 initialGas = gasleft();
```
this means that the sponsor has to pay the gas fee to complete the transfer or bridge for receivingUser, and the bridge transaction such as stargate bridge can be gas intensive. https://etherscan.io/txs?a=0x8731d54E9D02c286767d56ac03e8037C07e01e98&p=1999 this is an example of some swap transaction, bascially every swap cost roughly 20 USD gas fee, this basically mean that in mainnet, if on mainnet, if sponsor complete 10000 setupAndTrade transaction (10000 stargate bridge,) gas cost is not charged from the receivingUser, but paid from sponsor, then sponsor are lose 10000 * 20 USD = 200K USD fund. if (bridgeOp.inputToken == feesTokenAddress) { bridgeOp.amountIn = bridgeOp.amountIn - gasAmountCharged; } if (!inputFeeCharged) { bridgeOp.amountIn = bridgeOp.amountIn - feesDeductedFinal; } if (bridgeOp.inputToken != address(0)) { IERC20 tokenToBridge = IERC20(bridgeOp.inputToken); tokenToBridge.approve(markets[bridgeOp.exchangeID], bridgeOp.amountIn); } else { valueToSend = valueToSend; } bridge(bridgeOp, bridgeFeeEth + valueToSend); as we can see, if bridgeOp.inputToken is not feesTokenAddress, the gasAmountCharged is not really charged and deducted. Gas fee is charged too early and make sponsor lose fund when trigger setupAndTrade if there are bridging transaction.

## Recommendation
Charge additional gas to complete bridge transaction after bridging transaction.
