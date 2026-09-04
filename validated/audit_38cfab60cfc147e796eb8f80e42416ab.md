Based on the code analysis, the `EmporiumUpgradeable.sol::verifyWallet` function's EIP-712 signature binds exactly the values needed to constrain what the wallet owner authorized:

```
EMPORIUM_SIGNATURE_TYPEHASH: keccak256("EmporiumSignature(uint256 message,EmporiumOperation[] ops,uint256 maxFee,uint256 deadline)...")
``` [1](#0-0) 

**Checking the claimed equality**: `(assets leaving the wallet, their destination) == (ops, maxFee) the owner signed`.

1. **The `ops` (endpoint, invokeWallet, value, callData) are fully hashed via `_hashEmporiumOps`** and bound into the signed message, so any tampering with what the wallet is instructed to call invalidates the signature (`recoveredAddress == stack.signerAddress` check fails). [2](#0-1) 

2. **Fee extracted from the signer's wallet is capped by `maxFee`.** When `stack.signerAddress != address(0)`, `payRelayFees` only uses `flatFee` (never `variableRate`), and `verifyWallet` enforces `feeStructure.flatFee > stack.maxFee` reverts. So even though `circomData.feeStructure` (feeToken, relay, erc20TokenAddresses) is *not* part of the signed hash, the amount taken from the wallet can never exceed the owner-signed `maxFee`. [3](#0-2) 

3. **`circomData.relay` cannot be freely chosen by an unprivileged attacker.** `HinkalHelper.relayerIsValid` requires `tx.origin == relay` and `isRelayInList(relay)` — i.e., the relay field must be a whitelisted relayer, which the rules explicitly place out of scope (attacker is "not... a whitelisted relay"). [4](#0-3) 

4. **The `usedMessages[emporiumMessage]` flag is set to `true` on first use, before signature verification even runs**, permanently preventing replay of that exact signed stack regardless of what other `CircomData` fields accompany it. Once consumed by any transaction in any block, subsequent attempts revert with `UsedMessage()`. This is a genuine one-time-use guard, not a reusable nonce — it cannot be "reused across many victims' flows" because it is tied to a specific signer's signature over specific `ops`/`maxFee`/`deadline`, and is burned after a single use. [5](#0-4) 

5. **`stack.signerAddress` itself cannot be spoofed**: `ECDSA.tryRecover` derives an address purely from the signature `(v,r,s)` and the hashed message; the check `recoveredAddress == stack.signerAddress` means an attacker cannot bind an arbitrary `signerAddress` to someone else's signature — they'd need that victim's actual private-key signature over the exact `ops`/`maxFee`/`deadline`/`message` tuple, which they don't have. [6](#0-5) 

No path lets an unprivileged attacker move wallet assets to a destination or under fee terms the owner's signature never authorized: `ops` are fully hash-bound, the fee is capped at the signed `maxFee`, the relay recipient must be a whitelisted relayer (out of scope), and the replay guard permanently blocks reuse of the exact signed stack. The unsigned `CircomData` fields (`feeStructure.feeToken`, `variableRate`, `erc20TokenAddresses`, `amountChanges`, `relay`) only affect Emporium's own internal accounting and require either a whitelisted relay or fall within the already-capped `flatFee`.

### No vulnerability found for this question.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-260)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L284-300)
```text
    function _hashEmporiumOps(
        EmporiumOperation[] memory ops
    ) private pure returns (bytes32) {
        bytes32[] memory opHashes = new bytes32[](ops.length);
        for (uint256 i = 0; i < ops.length; i++) {
            opHashes[i] = keccak256(
                abi.encode(
                    EMPORIUM_OPERATION_TYPEHASH,
                    ops[i].endpoint,
                    ops[i].invokeWallet,
                    ops[i].value,
                    keccak256(ops[i].callData)
                )
            );
        }
        return keccak256(abi.encodePacked(opHashes));
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
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

**File:** contracts/HinkalHelper.sol (L30-35)
```text
    function relayerIsValid(address relay) internal view {
        if (relay != address(0)) {
            require(tx.origin == relay, "Unauthorized relay");
            require(isRelayInList(relay), "Relay is not whitelisted");
        }
    }
```
