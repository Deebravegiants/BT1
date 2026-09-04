Confirmed: `HinkalWallet.doSendToRelay` has no restriction on the `relay` address or `erc20TokenAddress` beyond `onlyEmporium`, so whatever the caller of `runAction` puts in `circomData.relay` / `feeStructure.feeToken` is honored directly against the wallet's own held balance. [1](#0-0) 

### Title
Emporium relay-fee destination and fee token are unsigned, letting anyone reroute a wallet owner's authorized fee to themselves - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
The EIP-712 `EmporiumSignature` that a wallet owner signs only covers `emporiumMessage`, the hash of `ops`, `maxFee`, and `deadline`; it never binds `circomData.relay` or `feeStructure.feeToken`. [2](#0-1)  Because `payRelayFees` pays `circomData.relay` in `feeStructure.feeToken` out of the wallet's own balance via `IHinkalWallet(signerAddress).doSendToRelay`, whoever submits the still-unconsumed signed stack chooses the fee's destination and token, up to the signed `maxFee` cap, regardless of what the owner intended. [3](#0-2) 

### Finding Description
The invariant that should hold is: `(fee recipient, fee token, fee amount)` actually paid out of the wallet == `(fee recipient, fee token, fee amount)` the owner's EIP-712 signature authorized. This is broken because the signed typed-data only covers:
```
EMPORIUM_SIGNATURE_TYPEHASH: (emporiumMessage, hashEmporiumOps(ops), maxFee, deadline)
``` [4](#0-3) 

`verifyWallet` only checks the signature over this tuple, marks `emporiumMessage` used, checks `deadline`, and enforces `feeStructure.flatFee <= stack.maxFee` - it never checks `circomData.relay` or `feeStructure.feeToken` against anything the signer approved. [5](#0-4) 

`runAction` then calls `payRelayFees(circomData, stack.signerAddress, deltaAmountChanges)`. Inside, for the `signerAddress != address(0)` path (wallet-authorized flow), `relayFee = flatFee` and is sent via `payRelay -> sendToRelayFromWallet -> IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, erc20TokenAddress)`. [6](#0-5) 

`HinkalWallet.doSendToRelay` performs no check on `relay` or `erc20TokenAddress` beyond `onlyEmporium`; it simply transfers the wallet's own tokens to whatever `relay` is supplied. [1](#0-0) 

Since `circomData` (including `relay` and `feeStructure`) is supplied fresh by whoever calls `Hinkal.transact`/submits the proof - not signed by the wallet owner - an unprivileged attacker who obtains a valid, not-yet-consumed `EmporiumStack` (e.g., observed in a relay's pending mempool transaction, or received from a front-end/relay integration before broadcast) can front-run the legitimate submission with the identical `stack` (same `v,r,s,ops,maxFee,deadline`) but substitute:
- `circomData.relay = attacker`
- `feeStructure.feeToken = <any token the wallet holds>`
- `feeStructure.flatFee = stack.maxFee` (the maximum allowed by the check)

Because `usedMessages[emporiumMessage]` is a global one-time replay guard keyed only on the message ID and not on the specific `circomData` payload, the first submission - attacker's - consumes the nonce and the legitimate flow reverts with `UsedMessage`, while the attacker walks away with the wallet's `flatFee` in a token/recipient the owner never approved. If `feeStructure.feeToken` doesn't correspond to any token in `erc20TokenAddresses`, the `"Gas Token in Emporium is not found"` branch still forces payment of `flatFee` in that arbitrary token from the wallet. [7](#0-6) 

The circuit-verified `signedMessageHash` (bound to `erc20TokenAddresses`, `amountChanges`, nullifiers, etc., via `getSignedMessageHash`) governs the shielded-pool side of the transaction but has no relationship to `relay` or `feeStructure`, so it provides no protection here. [8](#0-7) 

### Impact Explanation
An attacker steals wallet-owner funds (up to `stack.maxFee` of any token the wallet holds) by rerouting the relay-fee payment to their own address and choosing the fee token, while the legitimate relay/dApp flow gets pre-empted (its submission reverts with `UsedMessage`). This matches "theft of protocol/relay fees ... executing calls or moving assets a wallet owner ... never authorised" (High impact). It is repeatable against every distinct signed `EmporiumStack` a victim produces, each time up to `maxFee` per stack, but each individual stack/nonce can only be exploited once (front-run before the legitimate use).

### Likelihood Explanation
Preconditions: attacker must observe/obtain a valid, unexpired, unconsumed signed `EmporiumStack` before it is consumed on-chain (e.g., via mempool monitoring or a relay/dApp that shares unsigned payloads before submission), and must be able to submit a transaction that front-runs the legitimate one. The attacker needs no special privileges - just the ability to call `Hinkal.transact` with attacker-chosen `circomData.relay`/`feeStructure` alongside the intercepted stack, and enough ETH/gas to win the race. This is feasible whenever `flatFee > 0` and `maxFee > 0`, which is presumably the normal fee-charging case.

### Recommendation
Bind `circomData.relay` and `feeStructure` (at least `feeToken` and `flatFee`) into the EIP-712 `EMPORIUM_SIGNATURE_TYPEHASH` that the wallet owner signs, so the signature commits to exactly who receives the fee and in what token, not just an upper bound on the amount. Alternatively, restrict `doSendToRelay`/`payRelayFees` to only pay a relay address and token pre-registered/allow-listed by the wallet owner at signing time.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a `HinkalWallet`, fund the wallet with `TokenX`.
2. Have the wallet owner sign a valid `EmporiumStack` (some benign `ops`, `maxFee = 100`, `deadline = far future`) intended to be relayed with `feeStructure.feeToken = TokenX`, `relay = legitimateRelay`.
3. As the attacker, before the legitimate submission lands, call `Hinkal.transact`/`runAction` with the same `stack` (same `v,r,s`) but `circomData.relay = attacker`, `feeStructure.flatFee = 100`, `feeStructure.feeToken = TokenX`.
4. Assert: `TokenX.balanceOf(attacker)` increased by 100 and `TokenX.balanceOf(legitimateRelay)` == 0.
5. Assert: legitimate relay's subsequent submission of the same `emporiumMessage` reverts with `UsedMessage`, proving the owner's signature never constrained `(relay, feeToken)` and the guard is per-message only, not per-agreed-terms.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L36-39)
```text
    bytes32 private constant EMPORIUM_SIGNATURE_TYPEHASH =
        keccak256(
            "EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)EmporiumOperation(address endpoint,bool invokeWallet,uint128 value,bytes callData)"
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-282)
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
