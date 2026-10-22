# [H] buyoutLien() will cause the vault to fail to pro-

## Summary
Severity: High
Contest weight: 0.7465
Dataset id: 17717
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
cessEpoch() LienToken#buyoutLien() did not reduce vault#liensOpenForEpoch when vault#processEpoch() will check vault#liensOpenForEpoch[currentEpoch] == uint256(0) so processEpoch() will fail. When create LienToken, vault#liensOpenForEpoch[currentEpoch] will ++ when repay or liquidate, vault#liensOpenForEpoch[currentEpoch] will -- and LienToken#buyoutLien() will transfer from vault to other receiver, so liensOpenForEpoch need reduce.
```solidity
function buyoutLien(ILienToken.LienActionBuyout calldata params) external {
    /**** tranfer but not liensOpenForEpoch-- *****/
    _transfer(ownerOf(lienId), address(params.receiver), lienId);
}
```
processEpoch() maybe fail

## Recommendation
```solidity
function buyoutLien(ILienToken.LienActionBuyout calldata params) external {
    //do decreaseEpochLienCount()
    address lienOwner = ownerOf(lienId);
    bool isPublicVault = IPublicVault(lienOwner).supportsInterface(
        type(IPublicVault).interfaceId
    );
    if (isPublicVault && !AUCTION_HOUSE.auctionExists(collateralId)) {
        IPublicVault(lienOwner).decreaseEpochLienCount(
            IPublicVault(lienOwner).getLienEpoch(lienData[lienId].start +
            lienData[lienId].duration)
        );
    }
    lienData[lienId].last = block.timestamp.safeCastTo32();
    lienData[lienId].start = block.timestamp.safeCastTo32();
    lienData[lienId].rate = ld.rate.safeCastTo240();
    lienData[lienId].duration = ld.duration.safeCastTo32();
    _transfer(ownerOf(lienId), address(params.receiver), lienId);
}
```
