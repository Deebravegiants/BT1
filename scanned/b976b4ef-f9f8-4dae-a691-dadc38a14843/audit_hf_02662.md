# [M] Lack Of Signature Size Verification Checks

## Summary
Severity: Medium
Contest weight: 0.1909
Dataset id: 14404
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Multiple instances of lack of signature’s size verification before use have been identified:
• tss/ws/server/handler.go does not have checks to verify if signature sigBytes is of sufficient size:
sigBytes, sigErr := hex.DecodeString(sig)
if pubErr != nil || sigErr != nil {
wm.logger.Error("hex decode error for pubkey or sig", "err", err)
return
digestBz := crypto.Keccak256Hash([]byte(timeStr)).Bytes()
if !crypto.VerifySignature(pubKeyBytes, digestBz, sigBytes[:64]) {
wm.logger.Error("illegal signature", "publicKey", pubKey, "time", timeStr, "signature", sig)
return
If the signature is not of sufficient length line [184] could result in an unhandled out-of-bounds panic.
• tss/manager/sign.go also does not implement size checks before slicing the signature array:
if !crypto.VerifySignature(poolPubKeyBz, digestBz, signResponse.Signature[:64]) {
log.Error("illegal signature")
return
If signResponse.Signature length is less than 64, then this slicing operation signResponse.Signature[:64] will
panic with out-of-bounds error.
• Function CompactSignature() in datalayr-mantle/common/contracts/utils.go also does not implement signature size checks on sig parameter, however, this particular function does not appear to be used anywhere in
the codebase:
func CompactSignature(sig []byte) [64]byte {
// Decompose sig
r := Copy32Byte(sig[:32])
s := Copy32Byte(sig[32:64])
v := sig[64]

## Recommendation
Implement additional checks on the signature length prior to taking a slice of the signature bytes or performing any
indexing operations.
Mantle L2 Rollup
