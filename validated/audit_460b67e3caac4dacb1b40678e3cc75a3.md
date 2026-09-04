### Title
Emporium wallet-fee EIP-712 signature omits relay address and fee token, letting anyone redirect a signer's Hinkal Wallet fee payment - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
The `Emporium` external action lets a user's `IHinkalWallet` be debited a relay fee via `doSendToRelay`, gated by an EIP-712 signature from `stack.signerAddress`. That signature only commits to the op list, `maxFee`, and `deadline` — it never commits to *which* `relay` address receives the funds nor *which* token (`feeToken`/`erc20TokenAddresses[i]`) is debited. Since `circomData.relay` and the token set are supplied by whoever submits the transaction (any unprivileged caller building `circomData`), the signer's authorization can be replayed with a different relay recipient and/or fee token than what was actually signed off on.

### Finding Description
`verifyWallet` recovers `stack.signerAddress` from an EIP-712 hash built only from `emporiumMessage`, the ops hash, `maxFee`, and `deadline`: [1](#0-0) 

The only fee guard tied to that signature is `circomData.feeStructure.flatFee > stack.maxFee`, which bounds the *raw numeric* flat fee but says nothing about which token it is denominated in or who receives it: [2](#0-1) 

When `signerAddress != address(0)`, `relayFee` is simply set to `flatFee` (bypassing the variable-rate calculation) and forwarded to `payRelay`, which — because `signerAddress != address(0)` — calls `sendToRelayFromWallet`, which invokes the signer's own wallet to push funds to `circomData.relay` in `erc20TokenAddress`: [3](#0-2) [4](#0-3) 

Both `circomData.relay` (the fee recipient) and `erc20TokenAddress` / `feeStructure.feeToken` (the debited token) are attacker-controlled inputs to `CircomData` that are hashed only into `calldataHash` (`CircomDataBuilder.getHashedCalldata1/2`) — a value that protects the on-chain equality check `Calldata Hash Integrity Check Failed`, but is *never* included in the value the wallet-owning signer actually signs: [5](#0-4) 

Because `runAction` is invoked through the generic `Hinkal.transact` → `_externalTransact` path, and because a caller only needs a *valid ZK proof for their own shielded UTXOs* (not the signer's wallet funds) plus a *previously-issued, still-valid EIP-712 signature* from the wallet owner (e.g., one legitimately given to a specific relay for a specific op set), the caller can resubmit that same signature with a different `circomData.relay` and/or `feeStructure.feeToken`, as long as the numeric `flatFee <= stack.maxFee` still holds. This breaks the equality "funds moved out of signer's wallet == funds the signer explicitly authorized (recipient + token)."

### Impact Explanation
This allows unauthorized movement of a Hinkal Wallet signer's funds: an attacker can cause `doSendToRelay` to pay the flat fee to an attacker-chosen `relay` address instead of the intended relay, and/or in an attacker-chosen `feeToken` that may be far more valuable than what the signer intended to pay (the `maxFee` bound is purely numeric and token-agnostic). This is theft of protocol/relay fees redirected to an unauthorized recipient, and unauthorized asset movement from a wallet the signer never approved for that specific recipient/token — matching the High-impact category "theft or permanent freezing of protocol/relay fees ... executing calls or moving assets a wallet owner or prover never authorised."

### Likelihood Explanation
Likelihood is moderate: it requires an attacker to observe or intercept a validly signed Emporium message (which is plausible since these signatures are meant to be relayed/broadcast by third-party relays as part of normal operation) and resubmit it with modified `relay`/`feeToken` fields while keeping `flatFee <= maxFee`. No relayer/admin privilege is required — only crafting `circomData` and reusing the previously obtained signature, which is within reach of any unprivileged caller who can observe the signed payload in transit.

### Recommendation
Include `circomData.relay` and `circomData.feeStructure.feeToken` (and ideally `erc20TokenAddresses`) inside the EIP-712 `EMPORIUM_SIGNATURE_TYPEHASH` digest that `stack.signerAddress` signs, so the signer explicitly authorizes both the fee recipient and the fee-denominating token, not just a numeric cap.

### Proof of Concept
1. Signer `S` signs an Emporium `EmporiumSignature` message authorizing certain `ops`, with `maxFee = 100` and no explicit `relay`/`feeToken` binding (since these are not part of the signed struct).
2. Alice (the intended relay) is given this signature to submit `circomData` with `relay = Alice`, `feeStructure.feeToken = USDC`, `flatFee = 100`.
3. Before Alice submits, Eve intercepts the signature and instead submits her own `circomData` with identical `ops`, `emporiumMessage`, `maxFee`, `deadline` (so the ECDSA recovery in `verifyWallet` still succeeds) but `relay = Eve`, `feeStructure.feeToken = <high-value token S also holds>`, `flatFee = 100`.
4. `verifyWallet` passes because it never checked `relay`/`feeToken` against the signature; `payRelayFees` → `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(S).doSendToRelay(Eve, 100, <high-value token>)` executes, sending S's high-value token to Eve instead of the intended USDC-to-Alice payment. [2](#0-1)

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L186-199)
```text
    function sendToRelayFromWallet(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address feeToken
    ) internal {
        if (relayFee > 0) {
            IHinkalWallet(signerAddress).doSendToRelay(
                relay,
                relayFee,
                feeToken
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L200-260)
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

            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }

        if (!foundToken && feeStructure.flatFee != 0) {
            require(
                signerAddress != address(0),
                "Gas Token in Emporium is not found"
            );

            payRelay(
                circomData.relay,
                signerAddress,
                feeStructure.flatFee,
                feeStructure.feeToken
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L262-282)
```text
    function payRelay(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address erc20TokenAddress
    ) internal {
        if (relay == address(0) || relayFee == 0) {
            return;
        }

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

**File:** contracts/CircomDataBuilder.sol (L20-54)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }

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
