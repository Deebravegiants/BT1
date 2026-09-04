### Title
Emporium signer signature omits `feeStructure.feeToken`/`flatFee`/`circomData.relay`, letting a whitelisted relay redirect an arbitrary-token fee drain from the signer's `HinkalWallet` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When a user authorizes an Emporium batch via off-chain EIP-712 signature (`EMPORIUM_SIGNATURE_TYPEHASH`), the signed payload only commits to `emporiumMessage`, the hash of `ops` (endpoint/invokeWallet/value/callData), `maxFee`, and `deadline`. The actual fee token, fee amount computation path, and destination relay address are taken from `circomData.feeStructure` and `circomData.relay`, which are **not** part of the signed message. A relay building the outer `transact()` call can therefore charge the fee in a completely different (arbitrary, high value) ERC20 than what the signer intended, draining it from the signer's persistent `HinkalWallet` even when that token is unrelated to the signed `ops`.

### Finding Description
`verifyWallet()` recovers `stack.signerAddress` from an EIP-712 signature over:
```solidity
keccak256(abi.encode(EMPORIUM_SIGNATURE_TYPEHASH, circomData.emporiumMessage, _hashEmporiumOps(stack.ops), stack.maxFee, stack.deadline))
``` [1](#0-0) 
and only checks `circomData.feeStructure.flatFee > stack.maxFee` as a numeric cap: [2](#0-1) 

Neither `feeStructure.feeToken`, `feeStructure.variableRate`, nor `circomData.relay` is part of the signed struct, so the signer's authorization does not bind them. `payRelayFees()` then unconditionally force-charges `feeStructure.flatFee` of `feeStructure.feeToken` from the signer's wallet whenever that token isn't among the operation's own `erc20TokenAddresses`:
```solidity
if (!foundToken && feeStructure.flatFee != 0) {
    require(signerAddress != address(0), "Gas Token in Emporium is not found");
    payRelay(circomData.relay, signerAddress, feeStructure.flatFee, feeStructure.feeToken);
}
``` [3](#0-2) 
`payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)`, which the `HinkalWallet` executes unconditionally for its `onlyEmporium` caller with no further validation of token/amount/destination: [4](#0-3) 

`circomData.feeStructure` and `circomData.relay` are covered only by `calldataHash`/`getHashedCalldata2` and the ZK public-input vector via `formBasicInput`/`getSignedMessageHash`, not by the wallet signer's EIP-712 signature: [5](#0-4) 
That hash binds the *relay/msg.sender submitting the tx* (via `dimensionsCheck`/`performHinkalChecks`), not the wallet signer who authorized `ops`/`maxFee`/`deadline`. Since a whitelisted relay (`relayerIsValid` only requires `tx.origin == relay` and relay-list membership) is the one assembling the full `circomData`, it can freely pick `feeStructure.feeToken` to be any ERC20 the signer's `HinkalWallet` holds, set `flatFee == stack.maxFee` (the check is strict `>`, so equality passes), and route it to itself via `circomData.relay`, all while reusing an off-chain signature that never named that token, amount semantics, or destination.

### Impact Explanation
This breaks the equality "assets moved from the signer's wallet == assets the signer's signature authorized." The wallet-signer flow is meant to let a persistent `HinkalWallet` authorize a specific batch of DeFi calls up to a fee cap; instead, a relay can extract `maxFee` units of an arbitrary, possibly high-value ERC20 token from that wallet on every signed message, regardless of what the signed `ops` actually touch. This is unauthorized asset movement from a user-controlled wallet — funds are drained to a party (the relay) the signer never authorized to receive that specific token/amount, satisfying the High-impact criterion of "executing calls or moving assets a wallet owner or prover never authorised" (and can approach Critical if the extracted token's value greatly exceeds the intended fee).

### Likelihood Explanation
The attack requires only being (or colluding with) a currently whitelisted relay — no admin/owner keys, no upgrade access, and no cooperation from the signer beyond their pre-existing valid signature for an unrelated batch of ops. Since relays are operationally involved in submitting every `transact()` call and construct `circomData` themselves, this is a realistic, low-friction path rather than a purely theoretical one.

### Recommendation
Include `feeStructure` (feeToken, flatFee, variableRate) and `circomData.relay` (or a commitment to them) inside the EIP-712 `EMPORIUM_SIGNATURE_TYPEHASH` payload that the wallet signer signs, so the fee token, rate, and destination are cryptographically bound to the signer's authorization rather than left to the submitting relay's discretion.

### Proof of Concept
1. Signer's `HinkalWallet` holds token `T` (unrelated to any Emporium op) plus token `U` used in a batch of `ops`.
2. Signer signs an `EmporiumStack` with `ops` touching only `U`, `maxFee = M`, `deadline = D`.
3. A whitelisted relay builds `circomData` for this batch but sets `feeStructure.feeToken = T`, `feeStructure.flatFee = M`, `circomData.relay = <relay address>`; `T` is absent from `erc20TokenAddresses` so `foundToken` is false in `payRelayFees`.
4. `verifyWallet()` passes (signature matches `ops`/`maxFee`/`deadline`; `flatFee (M) > maxFee (M)` is false, so no revert).
5. `payRelayFees()` hits the `!foundToken && flatFee != 0` branch and force-transfers `M` units of `T` from the signer's `HinkalWallet` to the relay via `doSendToRelay`, even though the signer never signed anything referencing `T`. [6](#0-5)

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L342-348)
```text
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
