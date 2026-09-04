### Title
Emporium wallet-signature does not bind `feeStructure.feeToken`, allowing an unauthorized token to be drained from a signer's `HinkalWallet` as "relay fee" - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
The Emporium meta-transaction flow lets a `HinkalWallet` owner authorize a batch of calls off-chain via an EIP-712 signature (`EMPORIUM_SIGNATURE_TYPEHASH`), which is later relayed on-chain by an arbitrary, unprivileged transaction submitter. That signature binds the ops, `maxFee` (a bare `uint256`) and `deadline`, but never binds which ERC20 token the flat relay fee is denominated in, nor the token's decimals/value. The submitter freely chooses `circomData.feeStructure.feeToken` when building the `CircomData` passed to `Hinkal.transact`, so `payRelayFees`/`doSendToRelay` can debit the wallet in an arbitrary, more valuable token, up to `maxFee` raw units, never approved by the signer.

### Finding Description
`EmporiumUpgradeable.verifyWallet` recovers the signer over: [1](#0-0) 

and its only fee-related constraint is a bare numeric comparison: [2](#0-1) 

`circomData.feeStructure` (which carries `feeToken`, `flatFee`, `variableRate`) is not part of `EMPORIUM_OPERATION_TYPEHASH` or `EMPORIUM_SIGNATURE_TYPEHASH`: [3](#0-2) 

`circomData.feeStructure` is only bound into `calldataHash`/`signedMessageHash`, which are verified against the transaction *submitter's* own ZK proof and message, not the wallet owner's secp256k1 signature: [4](#0-3) 

Because Emporium is designed for gasless/relayed execution, the entity that assembles `circomData` and submits `Hinkal.transact()` (the relay, or anyone holding a shielded balance / valid proof) is not required to be `stack.signerAddress`. `performHinkalChecks` only checks proof/calldata self-consistency and relayer validity, never that `feeStructure` matches what the wallet owner intended: [5](#0-4) 

At execution, `payRelayFees` selects `isFeeToken` purely from the attacker-controlled `feeStructure.feeToken`, and when `signerAddress != address(0)` charges the full numeric `flatFee` (unscaled by token decimals or price) directly from the wallet: [6](#0-5) 

That fee is then pulled straight out of the signer's `HinkalWallet` via `doSendToRelay`, a privileged wallet function gated only by `onlyEmporium` (i.e., it trusts whatever `feeStructure` Emporium was given, not the signer's actual approval of that token): [7](#0-6) [8](#0-7) 

This mirrors the report's root cause class: a value-bearing field (`feeStructure.feeToken`) that is acted upon during fund movement but sits outside the equality that is supposed to authorize the wallet action (the EIP-712 `signedMessageHash`/`EMPORIUM_SIGNATURE_TYPEHASH`), letting an unprivileged party redefine the semantics of an authorized numeric limit (`maxFee`) to target a different, more valuable asset.

### Impact Explanation
This is a direct, unauthorized asset movement out of a user's `HinkalWallet`: the signer authorized "pay at most `maxFee` units of the relay fee," but the actual token debited is chosen entirely by the transaction submitter, who may pick any ERC20 the wallet holds. If `maxFee` was set assuming a low-decimal/low-value stablecoin, applying that same raw integer to a high-value/low-decimal token (e.g. WBTC) can drain a disproportionate, unauthorized amount of the wallet's real holdings to the relay address. This is theft of user funds via a wallet operation the signer never authorized, and it also lets a relay pay itself in whatever token it prefers regardless of the signer's fee-token preference (theft/misdirection of protocol/relay fees).

### Likelihood Explanation
Any account that can submit `Hinkal.transact()` for an Emporium `runAction` (with a legitimately obtained/leaked `EmporiumStack` signature and a valid ZK proof) can trigger this — no admin, relay-owner or wallet-owner key is required, and the flow is explicitly designed so the submitter and the wallet's EIP-712 signer can be different parties (that's the entire point of the gasless-relay design). The only pre-condition is that the target `HinkalWallet` holds some balance of another ERC20 the attacker chooses as `feeToken`, which is a normal state for an active wallet.

### Recommendation
Include `circomData.feeStructure` (at minimum `feeToken`, and ideally `flatFee`/`variableRate`) inside `EMPORIUM_OPERATION_TYPEHASH`/`EMPORIUM_SIGNATURE_TYPEHASH` so the wallet owner explicitly signs off on the exact fee token and amount, instead of only bounding a token-agnostic numeric `maxFee`.

### Proof of Concept
1. Wallet owner signs an `EmporiumStack` (via `EMPORIUM_SIGNATURE_TYPEHASH`) authorizing some ops with `maxFee = 5_000_000` (intended as 5 USDC, 6 decimals), `deadline` in the future.
2. Attacker (any address able to submit a valid Hinkal proof/`circomData`, not necessarily the signer or a whitelisted relay owner) builds `circomData.feeStructure = { feeToken: WBTC, flatFee: 5_000_000, variableRate: 0 }` and calls `Hinkal.transact(...)` targeting the Emporium `runAction` with `stack.signerAddress` set to the victim wallet and the previously obtained valid `(v, r, s)`.
3. `verifyWallet` only checks `flatFee (5_000_000) <= maxFee (5_000_000)` — passes, since `feeToken` was never signed.
4. `payRelayFees` → `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, 5_000_000, WBTC)` executes, transferring 0.05 WBTC (worth far more than the intended 5 USDC) from the victim's `HinkalWallet` to `circomData.relay`, which the attacker controls or colludes with. [9](#0-8)

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L31-39)
```text
    bytes32 private constant EMPORIUM_OPERATION_TYPEHASH =
        keccak256(
            "EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L219-244)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-328)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L346-348)
```text
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

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
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
