# [M] Nonce ordering of EOA can be updated to "arbitary" through an L1 tx

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-zksync
Published: 2023-10-23
Source: https://github.com/code-423n4/2023-10-zksync-findings/issues/861
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-10-zksync/blob/1fb4649b612fac7b4ee613df6f6b7d921ddd6b0d/code/system-contracts/contracts/ContractDeployer.sol#L68-L84


# Vulnerability details

## Impact
Nonce order of an EOA should always be sequetial, otherwise the transaction cannot be validated. The default account does not allow user to call function updateNonceOrdering of ContractDeployer, However, the restriction can be bypassed if user call updateNonceOrdering through an L1 priority transaction. As a result, the user's account will be permanently frozen.

## Proof of Concept
    function _validateTransaction(
        bytes32 _suggestedSignedHash,
        Transaction calldata _transaction
    ) internal returns (bytes4 magic) {
        // Note, that nonce holder can only be called with "isSystem" flag.
        SystemContractsCaller.systemCallWithPropagatedRevert(
            uint32(gasleft()),
            address(NONCE_HOLDER_SYSTEM_CONTRACT),
            0,
            abi.encodeCall(INonceHolder.incrementMinNonceIfEquals, (_transaction.nonce))
        );

    function incrementMinNonceIfEquals(uint256 _expectedNonce) external onlySystemCall {
        uint256 addressAsKey = uint256(uint160(msg.sender));
        uint256 oldRawNonce = rawNonces[addressAsKey];

        (, uint256 oldMinNonce) = _splitRawNonce(oldRawNonce);
        require(oldMinNonce == _expectedNonce, "Incorrect nonce");

        unchecked {
            rawNonces[addressAsKey] = oldRawNonce + 1;
        }
    }
incrementMinNonceIfEquals is used in _validateTransaction. it always uses sequential nonce.

            // Checks whether the nonce `nonce` have been already used for 
            // account `from`. Reverts if the nonce has not been used properly.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-zksync-findings/issues/861_
