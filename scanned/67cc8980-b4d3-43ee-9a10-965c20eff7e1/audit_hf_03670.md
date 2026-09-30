# [H] HatsSignerGate + MultiHatsSignerGate: more signers than expected

## Summary
Severity: High
Contest weight: 0.8057
Dataset id: 19759
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HatsSignerGate.claimSigner and MultiHatsSignerGate.claimSigner functions allow users to become signers.
It is important that both functions do not allow that there exist more valid signers than maxSigners.
This is because if there are more valid signers than maxSigners, any call to HatsSignerGateBase.reconcileSignerCount reverts, which means that no transactions can be executed.
The only possibility to resolve this is for a valid signer to give up his signer hat. No signer will voluntarily give up his signer hat. And it is wrong that a signer must give it up. Valid signers that have claimed before maxSigners was reached should not be affected by someone trying to become a signer and exceeding maxSigners. In other words the situation where one of the signers needs to give up his signer hat should have never occurred in the first place.
Think of the following scenario:
1. maxSignatures=10 and there are 10 valid signers
2. The signers execute a transaction that calls Safe.addOwnerWithThreshold such that there are now 11 owners (still there are 10 valid signers)
3. One of the 10 signers is no longer a wearer of the hat and reconcileSignerCount is called. So there are now 9 valid signers and 11 owners
4. The signer that was no longer a wearer of the hat in the previous step now wears the hat again. However reconcileSignerCount is not called. So there are 11 owners and 10 valid signers. The HSG however still thinks there are 9 valid signers.
When a new signer now calls claimSigner, all checks will pass and he will be swapped for the owner that is not a valid signer:
```solidity
// 9 >= 10 is false
if (currentSignerCount >= maxSigs) {
    revert MaxSignersReached();
}
// msg.sender is a new signer so he is not yet owner
if (safe.isOwner(msg.sender)) {
    revert SignerAlreadyClaimed(msg.sender);
}
// msg.sender is a valid signer, he wears the signer hat
if (!isValidSigner(msg.sender)) {
    revert NotSignerHatWearer(msg.sender);
}
```
So there are now 11 owners and 11 valid signers. This means when reconcileSignerCount is called, the following lines cause a revert:
```solidity
function reconcileSignerCount() public {
    address[] memory owners = safe.getOwners();
    uint256 validSignerCount = _countValidSigners(owners);
    // 11 > 10
    if (validSignerCount > maxSigners) {
        revert MaxSignersReached();
    }
```
As mentioned before, we end up in a situation where one of the valid signers has to give up his signer hat in order for the HSG to become operable again.
So one of the valid signers that has rightfully claimed his spot as a signer may lose his privilege to sign transactions.

## Recommendation
The HatsSignerGate.claimSigner and MultiHatsSignerGate.claimSigner functions should call reconcileSignerCount such that they work with the correct amount of
```diff
diff --git a/src/HatsSignerGate.sol b/src/HatsSignerGate.sol
index 7a02faa..949d390 100644
--- a/src/HatsSignerGate.sol
+++ b/src/HatsSignerGate.sol
@@ -34,6 +34,8 @@ contract HatsSignerGate is HatsSignerGateBase {
/// @notice Function to become an owner on the safe if you are wearing the signers hat
/// @dev Reverts if `maxSigners` has been reached, the caller is either invalid or has already claimed. Swaps caller with existing invalid owner if relevant.
function claimSigner() public virtual {
+   reconcileSignerCount();
+   uint256 maxSigs = maxSigners; // save SLOADs
    uint256 currentSignerCount = signerCount;
```
```diff
diff --git a/src/MultiHatsSignerGate.sol b/src/MultiHatsSignerGate.sol
index da74536..57041f6 100644
--- a/src/MultiHatsSignerGate.sol
+++ b/src/MultiHatsSignerGate.sol
@@ -39,6 +39,8 @@ contract MultiHatsSignerGate is HatsSignerGateBase {
/// @dev Reverts if `maxSigners` has been reached, the caller is either invalid or has already claimed. Swaps caller with existing invalid owner if relevant.
/// @param _hatId The hat id to claim signer rights for
function claimSigner(uint256 _hatId) public {
+   reconcileSignerCount();
+   uint256 maxSigs = maxSigners; // save SLOADs
    uint256 currentSignerCount = signerCount;
```
