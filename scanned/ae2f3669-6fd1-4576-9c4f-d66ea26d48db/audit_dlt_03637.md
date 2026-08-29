# [M] M-03 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-ambire-mitigation
Published: 2023-06-21
Source: https://github.com/code-423n4/2023-06-ambire-mitigation-findings/issues/19
Type: code-finding

## Details
# Lines of code

https://github.com/AmbireTech/ambire-common/blob/v2/contracts/AmbireAccount.sol#L131-L191


# Vulnerability details

# [adriro-MR-M-03-ERROR]: Recovery transaction can be replayed after a cancellation

The mitigation of M-03 contains an error in the implementation of the fix. The original issue is still present.

## Impact

The report in M-03 describes an issue related to the replay of the recovery transaction. After a cancellation is executed, the same transaction that initiated the recovery procedure can be replayed since the nonce is not incremented after canceling the recovery.

The intended fix is present in commit [1c0b06fbbbdd9aac1285d4fc4949f5b84f923238](https://github.com/AmbireTech/ambire-common/commit/1c0b06fbbbdd9aac1285d4fc4949f5b84f923238). The updated implementation of `execute()` is as follows:

https://github.com/AmbireTech/ambire-common/blob/v2/contracts/AmbireAccount.sol#L131-L191

```solidity
131: 	function execute(Transaction[] calldata calls, bytes calldata signature) public payable {
132: 		uint256 currentNonce = nonce;
133: 		// NOTE: abi.encode is safer than abi.encodePacked in terms of collision safety
134: 		bytes32 hash = keccak256(abi.encode(address(this), block.chainid, currentNonce, calls));
135: 
136: 		address signerKey;
137: 		// Recovery signature: allows to perform timelocked calls
138: 		uint8 sigMode = uint8(signature[signature.length - 1]);
139: 
140: 		if (sigMode == SIGMODE_RECOVER || sigMode == SIGMODE_CANCEL) {
141: 			(bytes memory sig, ) = SignatureValidator.splitSignature(signature);
142: 			(RecoveryInfo memory recoveryInfo, bytes memory innerRecoverySig, address signerKeyToRecover) = abi.decode(
143: 				sig,
144: 				(RecoveryInfo, bytes, address)
145: 			);
146: 			signerKey = signerKeyToRecover;
147: 			bool isCancellation = sigMode == SIGMODE_CANCEL;
148: 			bytes32 recoveryInfoHash = keccak256(abi.encode(recoveryInfo));
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-06-ambire-mitigation-findings/issues/19_
