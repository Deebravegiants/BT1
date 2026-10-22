# [H] Wrong withdraw address verification in NativeVaultLib.validateWithdrawalCredentials()

## Summary
Severity: High
Contest weight: 0.5567
Dataset id: 13971
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In NativeVaultLib.validateWithdrawalCredentials() the withdraw credential verification is the following:
```solidity
if (
    BeaconProofs.getWithdrawalCredentials(validatorFieldsProof.validatorFields)
    != bytes32(abi.encodePacked(bytes1(uint8(1)), bytes11(0), address(this)))
) {
    revert WithdrawalCredentialsMismatchWithNode();
}
```
First two parameters supplied to abi.encodePacked() are the prefix 0x01 and 11 zeros bytes as per the withdrawal credential spec, however, the last parameter is the withdrawal address which should be the Native Node, not the Native Vault.

## Recommendation
```diff
@@ -161,7 +164,7 @@ library NativeVaultLib {
    // Construct beacon chain withdraw address with current node's payable address
    if (
        BeaconProofs.getWithdrawalCredentials(validatorFieldsProof.validatorFields)
        != bytes32(abi.encodePacked(bytes1(uint8(1)), bytes11(0), address(this)))
+
        != bytes32(abi.encodePacked(bytes1(uint8(1)), bytes11(0), self.ownerToNode[nodeOwner].nodeAddress))
```
