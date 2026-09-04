### Title
Emporium relay fee token & destination are excluded from the signer's EIP-712 digest, letting the transaction submitter redirect wallet fee payments - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.verifyWallet` binds a `HinkalWallet` owner's authorization only to `emporiumMessage`, the hash of `ops`, `maxFee` and `deadline`. It never includes `circomData.relay` or `circomData.feeStructure.feeToken` in the signed digest, yet both fields are used afterward to pull tokens directly out of the signer's wallet via `doSendToRelay`.

### Finding Description
`verifyWallet` computes the EIP-712 digest strictly from the `EMPORIUM_SIGNATURE_TYPEHASH` fields: [1](#0-0) 

`EMPORIUM_SIGNATURE_TYPEHASH` itself only commits to `message`, `ops`, `maxFee`, and `deadline`: [2](#0-1) 

The only extra constraint applied to `feeStructure` is that `flatFee` cannot exceed the signed `maxFee`: [3](#0-2) 

Neither `circomData.feeStructure.feeToken` nor `circomData.relay` is constrained by the signature. Both are then used in `payRelayFees` to actually move funds out of the wallet: [4](#0-3) 

For the stateful (wallet-backed) path, the amount debited is exactly `flatFee` (bounded by the signed `maxFee`), but the token and recipient are attacker-chosen: [5](#0-4) 

`sendToRelayFromWallet` unconditionally invokes `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)`; because `HinkalWallet` trusts calls coming from the registered `Emporium` external action (`onlyAllowedRecipient`), it performs the transfer without any additional check that `relay`/`feeToken` were part of what the wallet owner actually signed.

This is the same root-cause shape as the referenced `VE3DRewardPool.addReward()` bug: a value-routing parameter (`ve3Token`/here `feeToken` and `relay`) is accepted and later used to move balances, without being tied into the equality/commitment (there, `rewardTokens` bookkeeping; here, the EIP-712 signed struct) that is supposed to authorize which asset and which recipient can be moved.

### Impact Explanation
Any unprivileged party who assembles and submits the `transact()`/Emporium calldata (a relay, or any address relaying a signed `EmporiumStack` on behalf of a wallet owner) can set `circomData.relay` to an address they control and `feeStructure.feeToken` to any ERC-20 already present in `circomData.erc20TokenAddresses` for the operation, then collect up to the signer-approved `maxFee` worth of that token from the user's `HinkalWallet`-controlled balance — regardless of which relay/token the signer actually intended to pay. This is theft of protocol/relay fees (redirected away from the legitimate relay and/or paid in an unintended token), matching the "High — theft ... of protocol/relay fees" impact category.

### Likelihood Explanation
High. No admin/owner privilege is required — only the ability to submit a `transact()` call carrying a validly-signed `EmporiumStack` (which is the normal, expected way relays operate in this protocol) and to freely choose the non-signed `relay`/`feeToken` fields of `circomData`. The wallet owner's signature gives no visibility into or control over these two fields.

### Recommendation
Include `feeStructure.feeToken` (and ideally `feeRecipient`/`relay`) inside `EMPORIUM_SIGNATURE_TYPEHASH` so the signer explicitly authorizes which token and which relay/recipient can receive the fee, mirroring the `addReward` fix recommendation of validating/binding all value-routing parameters before they are used to move balances.

### Proof of Concept
1. A `HinkalWallet` owner signs an `EmporiumStack` off-chain, authorizing `ops`, `maxFee = 100`, and `deadline`. They intend the relay fee to be paid in `USDC` to relay `R`.
2. A relay (or any party) who obtains this signature builds the actual `transact()` call, setting `circomData.relay = attacker`, and `circomData.feeStructure = { feeToken: DAI, flatFee: 100, ... }`, where `DAI` is also one of the tokens being withdrawn in the same operation (`deltaAmountChanges[i] < 0`).
3. `verifyWallet` accepts the signature because it never checked `feeToken` or `relay`, and `flatFee (100) <= maxFee (100)` passes.
4. `payRelayFees` -> `payRelay` -> `sendToRelayFromWallet` calls `IHinkalWallet(signerAddress).doSendToRelay(attacker, 100, DAI)`, pulling 100 `DAI` from the wallet and sending it to `attacker` instead of the intended relay `R` in the intended token `USDC`. [6](#0-5)

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L216-259)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-335)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L346-348)
```text
        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
```
