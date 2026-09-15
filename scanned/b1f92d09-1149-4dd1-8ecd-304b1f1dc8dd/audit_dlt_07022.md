# [M] M-03 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-ambire-mitigation
Published: 2023-06-21
Source: https://github.com/code-423n4/2023-06-ambire-mitigation-findings/issues/6
Type: code-finding

## Details
# Lines of code

https://github.com/AmbireTech/ambire-common/blob/455a8057e1e6edae48903fc9d116591b22fbf1c2/contracts/AmbireAccount.sol#L168-L171


# Vulnerability details

## Description
The problem identified by both wardens is the chance of using the initial signed recovery transaction to reinitialize the recovery procedure again after its cancellation, as long as this three transaction are done one after other.

However the recommendation to fix this issue was not followed and actually does not change at all the behavior of previous code.

## Impact
Reported issue is not fixed

## POC
The actual mitigation done does not follow the suggested mitigation given in the audit considering [issue 16](https://github.com/code-423n4/2023-05-ambire-findings/issues/16) and its duplication. The root reason of the issue reported was [this line](https://github.com/AmbireTech/ambire-common/blob/5c54f8005e90ad481df8e34e85718f3d2bfa2ace/contracts/AmbireAccount.sol#L178), given that its execution inside [else block](https://github.com/AmbireTech/ambire-common/blob/5c54f8005e90ad481df8e34e85718f3d2bfa2ace/contracts/AmbireAccount.sol#L160-L179) would prevent us to [increase the nonce](https://github.com/AmbireTech/ambire-common/blob/5c54f8005e90ad481df8e34e85718f3d2bfa2ace/contracts/AmbireAccount.sol#L189) later.

The nonce addition added in the new code is actually a meaningless operation which just waste gas. Next code shows and explain the error done by ambire team when they tried to fix the issue (it is the original code given to audit plus comments):

```solidity
	// @notice execute: this method is used to execute a single bundle of calls that are signed with a key
	// that is authorized to execute on this account (in `privileges`)
	// @dev: WARNING: if the signature of this is changed, we have to change AmbireAccountFactory
	function execute(Transaction[] calldata txns, bytes calldata signature) public payable {
		uint256 currentNonce = nonce;
		// NOTE: abi.encode is safer than abi.encodePacked in terms of collision safety
		bytes32 hash = keccak256(abi.encode(address(this), block.chainid, currentNonce, txns));

		address signerKey;
		// Recovery signature: allows to perform timelocked txns
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
                // @audit Here we are executing and scheduled recovery
				require(block.timestamp > scheduled, 'RECOVERY_NOT_READY');
                // @audit next commented line is the one added by ambire team, the nonce variable is updated, currentNonce does not change
                // nonce++;
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
                    // @audit Next is the line that was suggested to be added in the report
                    // nonce = currentNonce + 1;
					emit LogRecoveryCancelled(hash, recoveryInfoHash, recoveryKey, block.timestamp);
				} else {
					emit LogRecoveryScheduled(hash, recoveryInfoHash, recoveryKey, currentNonce, block.timestamp, txns);
				}
                // @audit Next line is the one that prevent us to increase the nonce previously
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
        // @audit Given that currentNonce was not modified, we have the same result with the new added line previously
		nonce = currentNonce + 1;
		executeBatch(txns);

		// The actual anti-bricking mechanism - do not allow a signerKey to drop their own privileges
		require(privileges[signerKey] != bytes32(0), 'PRIVILEGE_NOT_DOWNGRADED');
	}
```

## Recommended mitigation
In order to just solve the original issue, follow original recommended mitigation. However, original code has an issue that was not previously reported, and its mitigation step also solve this problem. The issue is reported in this contest as **Schedule recovery DOS by front-running with original schedule recovery transaction if no other transaction is executed**


## Assessed type

Other
