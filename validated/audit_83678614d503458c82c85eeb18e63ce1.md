### Title
Emporium proof-authorized operations have no on-chain deadline/fee-cap enforcement when `signerAddress == address(0)` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumStack` carries a `deadline` and `maxFee` that the prover embeds in `externalActionData.externalActionMetadata`, which is hashed into `calldataHash`/`signedMessageHash` and thus into the public-input vector that the ZK proof commits to. However, `verifyWallet()` only checks `block.timestamp > stack.deadline` (`SignatureExpired`) and `circomData.feeStructure.flatFee > stack.maxFee` (`FeeExceedsSignedMax`) when `stack.signerAddress != address(0)`. When `signerAddress == address(0)` (the "stateless"/proof-only path, i.e. `EmporiumOperation.invokeWallet == false` or no wallet delegate), the function returns immediately after marking the `emporiumMessage` as used, skipping both checks entirely.

### Finding Description
`verifyWallet` in `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`: [1](#0-0) 

only enforces `stack.deadline` and `stack.maxFee` inside the `if (stack.signerAddress == address(0)) { return; }` early-exit branch's *else* path — i.e. these checks are skipped whenever `signerAddress == address(0)`.

Meanwhile, `deadline` and `maxFee` are values inside `EmporiumStack`, which is ABI-decoded from `circomData.externalActionData.externalActionMetadata`: [2](#0-1) 

`externalActionData` (containing this metadata) is included in `getHashedCalldata2`, which forms `calldataHash`, which is itself folded into `getSignedMessageHash` and ultimately into the public-input vector fed to the SNARK verifier via `formBasicInput`: [3](#0-2) [4](#0-3) 

So the prover cryptographically commits to a specific `deadline`/`maxFee` when generating the proof, but the contract never checks these fields at execution time for the `signerAddress == address(0)` path. This breaks the equality between "what the prover authorized" (a time-bounded, fee-capped operation) and "what the contract actually enforces" (an operation executable at any future time, with any fee up to the actual `flatFee` charged, unbounded by `maxFee`). Any relay or holder of the once-generated proof/transaction payload can withhold it and submit it long after the intended deadline — after router/endpoint state, prices, or allowances have changed — executing arbitrary `op.endpoint.call{value: op.value}(op.callData)` against user-shielded funds held transiently in the Emporium contract.

This is a direct analog of the reported class: an authorization artifact (proposal / signed proof) has no expiration enforced on-chain, letting it be executed after an arbitrary delay in a way the original signer/prover did not intend when bounding it with a deadline.

### Impact Explanation
This qualifies as High severity under "executing calls or moving assets a wallet owner or prover never authorised": the prover explicitly bounded authorization with a `deadline` and `maxFee`, but the contract permits execution outside that bound for the signer-less path, allowing stale operations moving user shielded funds through arbitrary external calls, and allowing fee collection unbounded by the committed `maxFee`.

### Likelihood Explanation
Reaching this requires only that a proof be generated with `EmporiumOperation.invokeWallet == false` (or otherwise resulting in `stack.signerAddress == address(0)`), a legitimate, unprivileged usage path of `EmporiumUpgradeable.runAction`. No admin/relay privilege is needed to hold and later submit a previously generated valid proof/payload.

### Recommendation
Enforce `block.timestamp <= stack.deadline` and `feeStructure.flatFee <= stack.maxFee` unconditionally in `verifyWallet`, regardless of `stack.signerAddress`, since both fields are already committed into the proof's public inputs for every path.

### Proof of Concept
1. User generates a valid Hinkal proof for an Emporium action with `EmporiumStack{ signerAddress: address(0), ops: [...], maxFee: X, deadline: T }`, intending it to execute promptly (e.g., before `T`).
2. The relay/whoever holds the calldata does not submit it immediately.
3. At `block.timestamp > T` (well past `deadline`), the same calldata is submitted to `Hinkal`/`EmporiumUpgradeable.runAction`.
4. `verifyWallet` hits `if (stack.signerAddress == address(0)) { return; }` and returns without checking `deadline` or `maxFee`.
5. The proof still verifies (all committed values match), and `runAction` executes `op.endpoint.call{value: op.value}(op.callData)` using the user's shielded funds, at a time and under conditions the user never intended to authorize, with relay fees not bounded by the committed `maxFee`.

Note: I could not fully trace how/where `signerAddress == address(0)` is set in practice for a legitimate, unprivileged flow (e.g. whether front-end tooling always sets a real signer), which affects real-world likelihood; this should be verified against the off-chain proof-generation code, which is outside the indexed scope available to me.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-90)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
```text
    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
        }

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```

**File:** contracts/CircomDataBuilder.sol (L37-54)
```text
    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```

**File:** contracts/CircomDataBuilder.sol (L97-132)
```text
    function getSignedMessageHash(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256 emporiumMessage
    ) internal pure returns (uint256) {
        // split into two encode calls to avoid "stack too deep"
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
        uint256 hash2 = uint256(
            keccak256(
                abi.encode(
                    circomData.stealthAddressStructure.H1x,
                    circomData.stealthAddressStructure.H1y,
                    circomData.stealthAddressStructure.H0x,
                    circomData.stealthAddressStructure.H0y
                )
            )
        );
        return
            uint256(keccak256(abi.encode(hash1, hash2))) % CIRCOM_P;
    }
```
