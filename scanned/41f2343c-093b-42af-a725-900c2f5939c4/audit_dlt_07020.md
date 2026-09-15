# [M] M-03 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-ambire-mitigation
Published: 2023-06-21
Source: https://github.com/code-423n4/2023-06-ambire-mitigation-findings/issues/10
Type: code-finding

## Details
# Lines of code

https://github.com/AmbireTech/ambire-common/blob/f56e7dcaaa4ff8950b39fe6d5bced165d0f1c99f/contracts/AmbireAccount.sol#L131-L191


# Vulnerability details

## Impact
The [mitigation](https://github.com/AmbireTech/ambire-common/commit/1c0b06fbbbdd9aac1285d4fc4949f5b84f923238) updates the following `AmbireAccount.execute` function by adding `nonce++` in the `scheduled != 0 && !isCancellation` `if` block within the `sigMode == SIGMODE_RECOVER || sigMode == SIGMODE_CANCEL` `if` block. However, this does not fix [M-03: Recovery transaction can be replayed after a cancellation](https://github.com/code-423n4/2023-05-ambire-findings/issues/16). After a recovery is scheduled, the `AmbireAccount.execute` function can be called to cancel this scheduled recovery. For this cancellation, `scheduled != 0 && !isCancellation` is false because `sigMode == SIGMODE_CANCEL` and `isCancellation` are true. This means that `nonce++`, which would be executed in such `scheduled != 0 && !isCancellation` `if` block, is not executed; in the counterpart `else` block, `delete scheduledRecoveries[hash]` is executed in the `isCancellation` `if` block but `nonce` still remains the same without being incremented when `return` is executed. Because `nonce` is not changed, although the scheduled recovery is removed, the `AmbireAccount.execute` function can be called to replay the same `calls` and `signature` inputs, which were previously used to schedule the recovery that is removed, and schedule the same recovery again.

Moreover, executing `nonce++` in the `scheduled != 0 && !isCancellation` `if` block within the `sigMode == SIGMODE_RECOVER || sigMode == SIGMODE_CANCEL` `if` block is redundant since `nonce = currentNonce + 1` would be executed after the `scheduled != 0 && !isCancellation` and `sigMode == SIGMODE_RECOVER || sigMode == SIGMODE_CANCEL` `if` blocks finish executing. For example, if `nonce` is 1 at this moment, then `uint256 currentNonce = nonce` would set `currentNonce` to 1, `nonce++` would increase `nonce` to 2, but `nonce = currentNonce + 1` would set `nonce` to 2 again.

https://github.com/AmbireTech/ambire-common/blob/f56e7dcaaa4ff8950b39fe6d5bced165d0f1c99f/contracts/AmbireAccount.sol#L131-L191
```solidity
	function execute(Transaction[] calldata calls, bytes calldata signature) public payable {
		uint256 currentNonce = nonce;
		// NOTE: abi.encode is safer than abi.encodePacked in terms of collision safety
		bytes32 hash = keccak256(abi.encode(address(this), block.chainid, currentNonce, calls));

		address signerKey;
		// Recovery signature: allows to perform timelocked calls
		uint8 sigMode = uint8(signature[signature.length - 1]);

		if (sigMode == SIGMODE_RECOVER || sigMode == SIGMODE_CANCEL) {
			(bytes memory sig, ) = SignatureValidator.splitSignature(signature);
			(RecoveryInfo memory recoveryInfo, bytes memory innerRecoverySig, address signerKeyToRecover) = abi.decode(
				sig,
				(RecoveryInfo, bytes, address)
			);
			signerKey = signerKeyToRecover;
			bool isCancellation = sigMode == SIGMODE_CANCEL;
			bytes32 recoveryInfoHash = keccak256(abi.encode(recoveryInfo));
			require(privileges[signerKeyToRecover] == recoveryInfoHash, 'RECOVERY_NOT_AUTHORIZED');

			uint256 scheduled = scheduledRecoveries[hash];
			if (scheduled != 0 && !isCancellation) {
				require(block.timestamp > scheduled, 'RECOVERY_NOT_READY');
				nonce++;
				delete scheduledRecoveries[hash];
				emit LogRecoveryFinalized(hash, recoveryInfoHash, block.timestamp);
			} else {
				bytes32 hashToSign = isCancellation ? keccak256(abi.encode(hash, 0x63616E63)) : hash;
				address recoveryKey = SignatureValidator.recoverAddrImpl(hashToSign, innerRecoverySig, true);
				bool isIn;
				for (uint256 i = 0; i < recoveryInfo.keys.length; i++) {
					if (recoveryInfo.keys[i] == recoveryKey) {
						isIn = true;
						break;
					}
				}
				require(isIn, 'RECOVERY_NOT_AUTHORIZED');
				if (isCancellation) {
					delete scheduledRecoveries[hash];
					emit LogRecoveryCancelled(hash, recoveryInfoHash, recoveryKey, block.timestamp);
				} else {
					scheduledRecoveries[hash] = block.timestamp + recoveryInfo.timelock;
					emit LogRecoveryScheduled(hash, recoveryInfoHash, recoveryKey, currentNonce, block.timestamp, calls);
				}
				return;
			}
		} else {
			signerKey = SignatureValidator.recoverAddrImpl(hash, signature, true);
			require(privileges[signerKey] != bytes32(0), 'INSUFFICIENT_PRIVILEGE');
		}

		// we increment the nonce to prevent reentrancy
		// also, we do it here as we want to reuse the previous nonce
		// and respectively hash upon recovery / canceling
		// doing this after sig verification is fine because sig verification can only do STATICCALLS
		nonce = currentNonce + 1;
		executeBatch(calls);

		// The actual anti-bricking mechanism - do not allow a signerKey to drop their own privileges
		require(privileges[signerKey] != bytes32(0), 'PRIVILEGE_NOT_DOWNGRADED');
	}
```

## Proof of Concept
The following steps can occur for the described scenario.
1. The `AmbireAccount.execute` function is called to schedule a recovery.
2. The `AmbireAccount.execute` function is called to cancel the recovery scheduled in Step 1.
3. Because `nonce` is not incremented in Step 2, the `AmbireAccount.execute` function can be called to replay the same `calls` and `signature` inputs used in Step 1 and schedule the same recovery again.

## Tools Used
VSCode

## Recommended Mitigation Steps
`nonce++` can be removed from the `scheduled != 0 && !isCancellation` `if` block within the `sigMode == SIGMODE_RECOVER || sigMode == SIGMODE_CANCEL` `if` block. Then, https://github.com/AmbireTech/ambire-common/blob/f56e7dcaaa4ff8950b39fe6d5bced165d0f1c99f/contracts/AmbireAccount.sol#L168-L171 can be updated to the following code.

```solidity
    if (isCancellation) {
        nonce++;
        delete scheduledRecoveries[hash];
        emit LogRecoveryCancelled(hash, recoveryInfoHash, recoveryKey, block.timestamp);
    } else {
```


## Assessed type

Other
