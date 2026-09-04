### Title
Relay-chosen `feeToken` is unauthenticated by the Emporium wallet signature, allowing a relay to drain wallet funds via a token-mismatched flat fee - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.verifyWallet` requires the wallet owner's EIP‑712 signature to cover only `emporiumMessage`, the hashed `ops`, `maxFee`, and `deadline`. The signature never commits to `circomData.feeStructure.feeToken`. Fee extraction later only checks that `flatFee <= maxFee` as a raw number, then pulls that many units of whatever `feeToken` was placed in `circomData` by the relay, directly out of the user's `HinkalWallet` via `doSendToRelay`. Because `maxFee` is unit-less and the token it refers to is never bound to the signature, a relay can redirect the fee to a far more valuable ERC-20 than the signer intended and still pass the `flatFee > stack.maxFee` check.

### Finding Description
In `verifyWallet`: [1](#0-0) 
the signed digest is built from `EMPORIUM_SIGNATURE_TYPEHASH`, which only encodes `message`, the hash of `ops`, `maxFee`, and `deadline`: [2](#0-1) 

`circomData.feeStructure` (which contains `feeToken`, `flatFee`, `variableRate`) is not part of this typed-data hash. It is only bound into the ZK `calldataHash`/`signedMessageHash` that is checked against the *shielded-pool owner's* EdDSA key, not against the wallet EOA's ECDSA signature that authorizes `doSendToRelay`: [3](#0-2) 

The wallet-fee payment path is: [4](#0-3) 
For the `signerAddress != address(0)` branch, `relayFee` is simply set to `flatFee` (no per-token scaling), and: [5](#0-4) 
calls `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, erc20TokenAddress)`, which unconditionally transfers `relayFee` units of `erc20TokenAddress` out of the user's wallet: [6](#0-5) 

The only guard against an oversized fee is the numeric comparison `flatFee > stack.maxFee` in `verifyWallet` (line 346), which is token-agnostic. Because `feeStructure.feeToken` is never included in the signer's typed-data hash, whoever assembles `circomData` (the relay) can pick any token from `circomData.erc20TokenAddresses` as the fee token while keeping `flatFee` numerically at or below the signed `maxFee`. This breaks the intended equality: "the value the signer authorized to be paid as a fee" vs. "the value actually removed from the wallet," since the same raw number can represent wildly different value depending on the token's decimals/price.

### Impact Explanation
This is a wallet-signer-unauthorized asset movement: the smart wallet (`HinkalWallet`) sends ERC‑20 tokens to the relay based on a fee cap the owner signed for one (implicit) token, but the relay determines the actual token charged, which was never part of the signed payload. A relay can set `feeToken` to a high-value/low-decimal asset present in the same operation's `erc20TokenAddresses` list and charge up to the full numeric `maxFee` in that asset, extracting far more economic value than the signer intended — this is theft of user/wallet funds by an unprivileged relay, matching the "temporary/permanent freezing" and "unauthorized asset movement" impact classes.

### Likelihood Explanation
The `circomData` (including `feeStructure`) is constructed off-chain by whoever submits the transaction, typically the relay itself; only the numeric `maxFee`, `deadline`, and `ops` are authenticated by the wallet signer's signature. Any relay routing a signed Emporium operation that touches multiple token types can trivially select the fee token from `erc20TokenAddresses`, so this does not require any special privilege beyond being the (unprivileged) tx-relayer submitting a legitimately signed operation.

### Recommendation
Include `circomData.feeStructure.feeToken` (and ideally `variableRate`) in the `EMPORIUM_SIGNATURE_TYPEHASH` payload so the signer explicitly authorizes which token the flat fee will be denominated/paid in, analogous to binding `validUntil`/`validAfter` into the signed digest in the referenced AtomWallet fix. Alternatively, restrict `feeToken` for wallet-authorized operations to one of the tokens explicitly referenced in the signed `ops`, and re-validate that binding on-chain.

### Proof of Concept
1. Wallet owner signs an `EmporiumSignature` authorizing `ops` that move token `A`, with `maxFee = 1_000_000` (intending this to be, e.g., 1 USDC at 6 decimals).
2. The submitting relay constructs `circomData` with `erc20TokenAddresses` including token `A` and token `B` (an 18-decimal, high-value token also touched by the transaction), and sets `feeStructure.feeToken = B`, `feeStructure.flatFee = 1_000_000`.
3. `verifyWallet` only checks `recoveredAddress == signerAddress` (valid, since `ops`/`maxFee`/`deadline` match what was signed) and `flatFee (1_000_000) <= maxFee (1_000_000)` — both pass.
4. `payRelayFees` → `sendToRelayFromWallet` → `HinkalWallet.doSendToRelay` transfers `1_000_000` units of token `B` (worth vastly more than the intended 1 USDC) from the user's wallet to the relay, without the token choice ever having been signed by the wallet owner.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-237)
```text
    function payRelayFees(
        CircomData calldata circomData,
        address signerAddress,
        int256[] calldata deltaAmountChanges
    ) internal {
        FeeStructure calldata feeStructure = circomData.feeStructure;

        bool foundToken = false;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }

            address erc20TokenAddress = circomData.erc20TokenAddresses[i];
            bool isFeeToken = erc20TokenAddress == feeStructure.feeToken;

            if (isFeeToken) {
                foundToken = true;
            }

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
            } else {
                relayFee = flatFee;
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L271-282)
```text

        if (signerAddress == address(0)) {
            sendToRelay(relay, relayFee, erc20TokenAddress);
        } else {
            sendToRelayFromWallet(
                relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-348)
```text
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
