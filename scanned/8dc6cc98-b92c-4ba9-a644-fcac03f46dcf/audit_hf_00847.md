# [H] Users redeeming early will with-

## Summary
Severity: High
Contest weight: 0.7806
Dataset id: 2583
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
VaultLib::redeemEarly() is called when users redeem early via Vault::redeemEarlyLv(), which allows users to redeem Lv for Ra and pay a fee. In the process, the Vault burns Ct and Ds in VaultLib::_redeemCtDsAndSellExcessCt() for Ra, by calling PsmLib::PsmLibrary.lvRedeemRaWithCtDs(). However, it never calls RedemptionAssetManagerLib::decLocked() to decrease the tracked locked Ra, but the Ra leaves the Vault for the user redeeming. This means that when a new Ds is issued in the PsmLib or users call PsmLib::redeemWithCt(), PsmLib::_separateLiquidity() will be called and it will calculated the exchange rate to withdraw Ra and Pa as if the Ra amount withdrawn earlier was still there. When it calls self.psm.balances.ra.convertAllToFree(), it converts the locked amount to free and assumes these funds are available, when in reality they have been withdrawn earlier. As such, the Ra and Pa checkpoint will be incorrect and users will redeem more Ra than they should, such that the last users will not be able to withdraw and the first ones will profit. In PsmLib.sol:125, self.psm.balances.ra.decLocked(amount); is not called. Internal pre-conditions None. External pre-conditions None. Attack Path 1. User calls Vault::redeemEarlyLv() or ModuleCore::issueNewDs() is called by the admin. Users withdraw more funds then they should via PsmLib::redeemWithCt() meaning the last users can not withdraw.

## Proof of Concept
PsmLib::lvRedeemRaWithCtDs() does not reduce the amount of Ra locked.
```solidity
function lvRedeemRaWithCtDs(State storage self, uint256 amount, uint256 dsId) internal {
    DepegSwap storage ds = self.ds[dsId];
    ds.burnBothforSelf(amount);
}
```

## Recommendation
PsmLib::lvRedeemRaWithCtDs() must reduce the amount of Ra locked.
```solidity
function lvRedeemRaWithCtDs(State storage self, uint256 amount, uint256 dsId) internal {
    self.psm.balances.ra.decLocked(amount);
    DepegSwap storage ds = self.ds[dsId];
    ds.burnBothforSelf(amount);
}
```
