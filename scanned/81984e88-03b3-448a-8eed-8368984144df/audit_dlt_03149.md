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
            function ensureNonceUsage(from, nonce, shouldNonceBeUsed) {
                // INonceHolder.validateNonceUsage selector
                mstore(0, {{RIGHT_PADDED_VALIDATE_NONCE_USAGE_SELECTOR}})
                mstore(4, from)
                mstore(36, nonce)
                mstore(68, shouldNonceBeUsed)

                let success := call(
                    gas(),
                    NONCE_HOLDER_ADDR(),
                    0,
                    0,
                    100,
                    0,
                    0
                )

                if iszero(success) {
                    revertWithReason(
                        ACCOUNT_TX_VALIDATION_ERR_CODE(),
                        1
                    )
                }
            }

    function validateNonceUsage(address _address, uint256 _key, bool _shouldBeUsed) external view {
        bool isUsed = isNonceUsed(_address, _key);

        if (isUsed && !_shouldBeUsed) {
            revert("Reusing the same nonce twice");
        } else if (!isUsed && _shouldBeUsed) {
            revert("The nonce was not set as used");
        }
    }

    function isNonceUsed(address _address, uint256 _nonce) public view returns (bool) {
        uint256 addressAsKey = uint256(uint160(_address));
        return (_nonce < getMinNonce(_address) || nonceValues[addressAsKey][_nonce] > 0);
    }
The bootloader calls validateNonceUsage too, which considers the arbitary ordering.

We need to prevent default account from changing nonce ordering type, otherwise these two methods will conflict. If user's current minNonce is 13, nonce of new tx also needs to be 13, but if some value is already stored under 14, isNonceUsed will return true. Which means the user will no longer be able to initiate new transactions.

    function _execute(Transaction calldata _transaction) internal {
        address to = address(uint160(_transaction.to));
        uint128 value = Utils.safeCastToU128(_transaction.value);
        bytes calldata data = _transaction.data;
        uint32 gas = Utils.safeCastToU32(gasleft());

        // Note, that the deployment method from the deployer contract can only be called with a "systemCall" flag.
        bool isSystemCall;
        if (to == address(DEPLOYER_SYSTEM_CONTRACT) && data.length >= 4) {
            bytes4 selector = bytes4(data[:4]);
            // Check that called function is the deployment method,
            // the others deployer method is not supposed to be called from the default account.
            isSystemCall =
                selector == DEPLOYER_SYSTEM_CONTRACT.create.selector ||
                selector == DEPLOYER_SYSTEM_CONTRACT.create2.selector ||
                selector == DEPLOYER_SYSTEM_CONTRACT.createAccount.selector ||
                selector == DEPLOYER_SYSTEM_CONTRACT.create2Account.selector;
        }
flag isSystemCall is only set true when calling deployment method of ContractDeployer, so if user tries to call function updateNonceOrdering of ContractDeployer, isSystemCall will be false and the call will fail.

            function msgValueSimulatorMimicCall(to, from, value, dataPtr) -> success {
                // Only calls to the deployer system contract are allowed to be system
                let isSystem := eq(to, CONTRACT_DEPLOYER_ADDR())

                success := mimicCallOnlyResult(
                    MSG_VALUE_SIMULATOR_ADDR(),
                    from, 
                    dataPtr,
                    0,
                    1,
                    value,
                    to,
                    isSystem
                )
            }
However, if the transaction is initiated on L1, selector is not checked. Flag isSystem is set true as long as the target is ContractDeployer. The transaction to updateNonceOrdering will succeed.

    function updateNonceOrdering(AccountNonceOrdering _nonceOrdering) external onlySystemCall {
        AccountInfo memory currentInfo = accountInfo[msg.sender];

        require(
            _nonceOrdering == AccountNonceOrdering.Arbitrary &&
                currentInfo.nonceOrdering == AccountNonceOrdering.Sequential,
            "It is only possible to change from sequential to arbitrary ordering"
        );

        currentInfo.nonceOrdering = _nonceOrdering;
        _storeAccountInfo(msg.sender, currentInfo);

        emit AccountNonceOrderingUpdated(msg.sender, _nonceOrdering);
    }
Once updated, the change is permanent. The account can no longer initiate any new transactions.

## Tools Used
Manual

## Recommended Mitigation Steps
Don't allow EOA to call updateNonceOrdering. Do the check on L1 side.


## Assessed type

Context
