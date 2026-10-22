# [M] VestingMaster: Banning account causes future rewards in RevenueSharingVault to get lost and tokens are stuck

## Summary
Severity: Medium
Contest weight: 0.1240
Dataset id: 16049
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for the owner of VestingMaster to ban accounts from calling IndividualVestingVault.claim(). As a result of this, the shares that belong to the banned account, are never withdrawn and just remain owned by IndividualVestingVault. This means that any revenue earned on these shares is lost forever.

## Recommendation
```diff
--- a/apps/contracts/src/Vesting/IndividualVestingVault.sol
+++ b/apps/contracts/src/Vesting/IndividualVestingVault.sol
@@ -42,6 +42,10 @@ contract IndividualVestingVault is VestingUtils, Initializable {
     tokenizedVault.withdraw(amountToClaim, msg.sender, address(this));
 }
+
+function banAccount() external onlyVestingMaster() {
+    tokenizedVault.redeem(tokenizedVault.balanceOf(address(this)), msg.sender, address(this));
+}
+
 function claimableTokenAmount() public view returns (uint256) {
     if (vaultIsBanned()) {
         return 0;
```
```diff
--- a/apps/contracts/src/Vesting/VestingMaster.sol
+++ b/apps/contracts/src/Vesting/VestingMaster.sol
@@ -36,9 +36,14 @@ contract VestingMaster is IVestingMaster, VestingUtils, Ownable, MinimalProxyFac
     }
 }
+
+function withdrawTornadoTokens(address recipient) external onlyOwner {
+    vestedToken.transfer(recipient, vestedToken.balanceOf(address(this)));
+}
+
 function banAccount(address account) external onlyOwner {
     require(!claimingIsProhibitedFor[account]);
     claimingIsProhibitedFor[account] = true;
+    vaultOf[account].banAccount();
 }
```
It is recommended to redeem the Vault shares for TRNDO and send them back to VestingMaster when an account is banned. Thereby, no TRNDO token get stuck and revenue is not lost.
