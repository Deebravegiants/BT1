### Title
Emporium wallet signature does not bind `feeStructure.feeToken`, letting the relay be paid the flat fee in any token the wallet holds - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` lets a `HinkalWallet` owner authorize a batch of DeFi operations by signing an EIP-712 `EmporiumSignature` that covers only `ops`, `maxFee`, and `deadline`. [1](#0-0)  When the wallet-based ("stateful") path is used, the relay fee charged to the wallet is `flatFee`, bounded only by `stack.maxFee`, but the *token* in which that fee is denominated (`circomData.feeStructure.feeToken`) is never included in the signed hash. [2](#0-1)  This mirrors the report's bug class: a value-bearing field (here, `feeStructure.feeToken`) is acted upon by the protocol (fee extraction from the wallet) without being part of the equality/authorization the signer actually agreed to.

### Finding Description
`verifyWallet` recovers the signer of `EMPORIUM_SIGNATURE_TYPEHASH`, which commits to `emporiumMessage`, the hash of `ops`, `maxFee`, and `deadline` only, and separately checks `circomData.feeStructure.flatFee <= stack.maxFee`. [3](#0-2)  Neither `feeStructure.feeToken` nor `circomData.erc20TokenAddresses` are part of the signed digest.

In `payRelayFees`, when `signerAddress != address(0)` (the stateful/wallet path), the code sets `relayFee = flatFee` for whichever `erc20TokenAddress` in `circomData.erc20TokenAddresses` matches `feeStructure.feeToken` and has a negative `deltaAmountChanges[i]` (i.e., a withdrawal out of the wallet/Emporium is already occurring for that token because of the requested ops), and this fee is pulled from the signer's wallet via `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay`. [4](#0-3) [5](#0-4)  The `HinkalWallet.doSendToRelay` executes an unconditional `sendToRelay` for whatever `erc20TokenAddress`/amount the Emporium instructs, once `onlyEmporium` is satisfied. [6](#0-5) 

Since `feeStructure` (including `feeToken`) is only bound into the *ZK-proof* `calldataHash` (via `getHashedCalldata2`), which is authorized by the shielded-note owner submitting the proof — a potentially different party from the wallet's signer — the wallet owner's EIP-712 approval never actually pins down which asset will be debited as the flat fee. [7](#0-6)  A prover who controls `circomData` (and therefore the ZK proof matching it) can pick `feeStructure.feeToken` to be any token that the requested `ops` cause to leave the wallet with a negative `deltaAmountChanges[i]`, while the wallet owner believed `maxFee` capped the cost in a specific (e.g., cheap/gas) token. The numeric cap (`maxFee`) is respected, but the token denomination is not — the wallet can be debited `flatFee` units of a far more valuable asset than the signer intended, since the signature never commits to `feeToken`.

### Impact Explanation
This breaks the equality the wallet owner actually authorized: "I approve these `ops` and will pay at most `maxFee`" is silently reinterpreted as "at most `maxFee` units of *any* token the ops happen to move out of my wallet." This is theft of protocol/relay fees at the wallet owner's expense beyond what they signed for — falling into the High-impact bucket ("theft ... of protocol/relay fees ... executing calls or moving assets a wallet owner or prover never authorised").

### Likelihood Explanation
Exploitation requires the party constructing `circomData` (the prover/transaction submitter) to be adversarial toward the wallet-signer, and for the requested `ops` to already produce a negative balance change in some valuable token from the wallet. In the intended Emporium use-case, the note owner and wallet owner are often the same actor, which would reduce likelihood; the report is only reachable when the two are distinct or when a malicious/cooperating third-party proof submitter is combined with a user's genuinely-signed `EmporiumSignature`.

### Recommendation
Include `circomData.feeStructure.feeToken` (and ideally the full `feeStructure`) inside the `EMPORIUM_SIGNATURE_TYPEHASH` digest that `stack.signerAddress` signs, so wallet owners explicitly authorize both the fee ceiling and the token it will be charged in.

### Proof of Concept
1. Wallet owner `W` signs an `EmporiumSignature` for `ops = [swap A→B on DEX X]`, `maxFee = 1e6` (intending this to be a small amount of a stablecoin), `deadline`.
2. A malicious prover (holding a valid shielded note, distinct from `W`) builds `circomData` with `feeStructure = {feeToken: <token B>, flatFee: 1e6, variableRate: 0}` and `erc20TokenAddresses` including token B with a negative `deltaAmountChanges` entry (since the swap already sends token B out of the wallet).
3. `runAction` executes the signed `ops`, then `payRelayFees` charges `flatFee` (1e6 units of token B, which may be worth far more than the stablecoin `W` expected) from `W`'s `HinkalWallet` to the relay via `doSendToRelay`, without any additional check that token B was the fee token `W` intended. [8](#0-7)

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L216-244)
```text
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

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L36-42)
```text
    function doSendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) external onlyEmporium {
        sendToRelay(relay, actualAmount, erc20TokenAddress);
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
