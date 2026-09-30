# [M] Tokens that revert of zero value

## Summary
Severity: Medium
Contest weight: 0.4266
Dataset id: 1937
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Tokens that revert of zero value transfers can cause reverts on liquidation breaks their contract pools. In multiple places token amount which can become zero is transferred without checking the value is zero. This will cause these transactions to revert.
ontracts/LenderCommitmentForwarder/extensions/LenderCommitmentGroup/LenderCommitmentGroup_Smart.sol#L699-L727
```solidity
IERC20(principalToken).safeTransferFrom(
    msg.sender,
    address(this),
    amountDue + tokensToTakeFromSender - liquidationProtocolFee
);
address protocolFeeRecipient =
    ITellerV2(address(TELLER_V2)).getProtocolFeeRecipient();
IERC20(principalToken).safeTransferFrom(
    msg.sender,
    address(protocolFeeRecipient),
    liquidationProtocolFee
);
totalPrincipalTokensRepaid += amountDue;
tokenDifferenceFromLiquidations += int256(tokensToTakeFromSender - liquidationProtocolFee);
} else {
    uint256 tokensToGiveToSender = abs(minAmountDifference);
    IERC20(principalToken).safeTransferFrom(
        msg.sender,
        address(this),
        amountDue - tokensToGiveToSender
    );
```
Internal pre-conditions
External pre-conditions
Attack Path
In case liquidation reverts (due to tokensToGiveToSender == -amountDue), the tokenDifferenceFromLiquidations won't be updated which will cause the value of the shares to be incorrectly high (because in reality the auction is settling at 0 price)

## Recommendation
Check if amount is non-zero before transferring
