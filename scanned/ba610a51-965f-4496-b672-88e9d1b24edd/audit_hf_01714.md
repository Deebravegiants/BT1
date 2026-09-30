# [H] H-4 DoS KintoWallet contract

## Summary
Severity: High
Contest weight: 0.7509
Dataset id: 9348
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• KintoWallet.sol#L235  
_resetSigners does not take into account the current SignerPolicy in any way. A user can accidentally call resetSigners with an array length of 1 (with current policy > 1). A sample code is below:  
```solidity
abi.encodeWithSignature(
    'resetSigners(address[])',
    [address1, address2]
)
abi.encodeWithSignature(
    'setSignerPolicy(uint8)',
    2
)
abi.encodeWithSignature(
    'resetSigners(address[])',
    [address1]
)
// _kintoWalletv1.signerPolicy() == 2
// _kintoWalletv1.getOwnersCount() == 1
```
Thus, the following code (KintoWallet.sol#L220) will be called:  
```solidity
else {
    (signatures[0], signatures[1], signatures[2]) =
        ByteSignature.extractThreeSignatures(
            userOp.signature);
}
for (uint i = 0; i < owners.length; i++) {
    if (
        owners[i] == hash.recover(signatures[i])
    ) {
        requiredSigners--;
    }
}
return requiredSigners;
```
and since owners.length == 1, the _validateSignature method will always return an error. You will need to wait for 7 days and restore the account (finishRecovery).

## Recommendation
We recommend that when calling resetSigners you also check the policy variable and adjust it if necessary.
