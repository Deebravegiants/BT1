# [M] Revisited Logic in PikaPerpV3::modifyMargin()

## Summary
Severity: Medium
Contest weight: 0.4381
Dataset id: 12749
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PikaPerpV3 protocol has the main PikaPerpV3 contract that manages the user positions. While examining a key routine to update a given position's margin, we notice the current implementation can be improved. Specifically, we show below the related implementation. While it properly achieves the tasked logic, we notice it does not ensure the position after the margin modification is healthy. This needs to be fixed so that the position after margin decrease should not be liquidatable!
```solidity
function modifyMargin(
    uint256 positionId,
    uint256 margin,
    bool shouldIncrease
) external payable nonReentrant {
    // Check position
    Position storage position = positions[positionId];
    require(msg.sender == position.owner || _validateManager(position.owner), "!allow");

    uint256 newMargin;
    if (shouldIncrease) {
        IERC20(token).uniTransferFromSenderToThis(margin * tokenBase / BASE);
        newMargin = uint256(position.margin) + margin;
    } else {
        newMargin = uint256(position.margin) - margin;
        IERC20(token).uniTransfer(msg.sender, margin * tokenBase / BASE);
    }

    // New position params
    uint256 newLeverage = uint256(position.leverage) * uint256(position.margin) / newMargin;
    require(newLeverage >= 1 * BASE, "!low -lev");
    position.margin = uint128(newMargin);
    position.leverage = uint64(newLeverage);
    emit ModifyMargin(
        positionId,
        msg.sender,
        position.owner,
        margin,
        newMargin,
        newLeverage,
        shouldIncrease
    );
}
```

## Recommendation
Revise the above affected routine to properly ensure the position is healthy after margin adjustment.
