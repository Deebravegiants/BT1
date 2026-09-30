# [M] RsaVerifyOptimized::pkcs1Sha256() modified the original code incorrectly in one instance

## Summary
Severity: Medium
Contest weight: 0.0970
Dataset id: 9322
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RsaVerifyOptimized::pkcs1Sha256() code has slight changes to the original code. There is one modification that is different from the original, which is checking if the first bytes of decipher are 0x00 and 0x01, respectively. As can be seen in the following code snippet, the first 2 bytes of decipher may be for example 0x0101 and it will not set the result to false.
if iszero(and(mload(add(decipher, 32)), 0x0001ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff)) {
result := false
}
Additionally, here should be 111, but the code is not reachable as it only accepts digestAlgoWithParamLen == 17 == sha256ExplicitNullParamByteLen.

## Recommendation
Use the previous optimized assembly code.
