### Title
Emporium relay-fee token not bound by the wallet owner's signature - unauthorised ERC20 drain from `HinkalWallet` - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`EmporiumUpgradeable.verifyWallet` implements a nonce (`usedMessages[circomData.emporiumMessage]`), so the guardian-signature-replay bug class from the external report does not directly transpose here — single-use of a given `emporiumMessage` is enforced. However, the analogous "authorisation is weaker than the action it green-lights" flaw exists one level down: the EIP-712 `EmporiumSignature` that the smart-contract wallet owner signs only commits to `(emporiumMessage, opsHash, maxFee, deadline)`. It does **not** commit to `circomData.feeStructure.feeToken`, `circomData.erc20TokenAddresses`, or `circomData.amountChanges`. Those fields are supplied by whoever calls `runAction` (the allowed-recipient/Hinkal-relay path) and are used, unchecked against the signature, to decide which ERC20 token is pulled out of the signer's `HinkalWallet`.

### Finding Description
`verifyWallet` recovers the signer over: [1](#0-0) 
i.e. `emporiumMessage`, the hash of `ops`, `maxFee`, and `deadline`. The `feeStructure` (which token and how much flat fee to charge) is never part of this hash — it comes straight from the `CircomData` passed into `runAction` by the caller.

`payRelayFees` then uses `circomData.feeStructure.feeToken` / `flatFee` directly: [2](#0-1) 

Notice the fallback branch: if none of `circomData.erc20TokenAddresses` equals `feeStructure.feeToken` (`foundToken == false`) and `flatFee != 0`, the code still calls `payRelay(circomData.relay, signerAddress, feeStructure.flatFee, feeStructure.feeToken)` with **no restriction that `feeStructure.feeToken` be one of the tokens involved in the signed `ops`**. `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, relayFee, feeToken)`: [3](#0-2) 

`HinkalWallet.doSendToRelay` unconditionally transfers `erc20TokenAddress` tokens out of the wallet to `relay` as long as the caller is the Emporium contract: [4](#0-3) 
and internally uses `Transferer.sendToRelay` → `transferERC20TokenOrETH`, which moves the wallet's own balance: [5](#0-4) 

Only the numeric bound `flatFee <= maxFee` is checked against the signature: [6](#0-5) 
The *identity* of the token being debited is entirely controlled by whichever `CircomData.feeStructure.feeToken` value the transaction submitter chooses — this is analogous to the report's core defect: a control value ("which token/action was authorised") is decoupled from the value that is actually checked ("a bare numeric cap"), so a party other than the signer can reuse a validly-signed authorization to move a different asset than the signer intended.

### Impact Explanation
An entity that can call `Hinkal`/the allowed-recipient path (a relay operator, or the prover assembling `circomData` for a given relay) can attach an arbitrary `feeStructure.feeToken` to a wallet-signed `EmporiumSignature`. As long as `feeStructure.flatFee <= stack.maxFee`, this silently drains up to `maxFee` units of any ERC20 token the `HinkalWallet` holds — a token the wallet owner never named or approved in the signature — to the relay. This is an unauthorised asset movement from a user's smart-contract wallet (`HinkalWallet`), executed via a token/action the signer never authorised, which meets the High-severity bar ("executing calls or moving assets ... a prover never authorised").

### Likelihood Explanation
Requires the ability to submit `CircomData` for a `runAction` call gated by `onlyAllowedRecipient` (i.e., control over what the relay/Hinkal core passes in), plus a `HinkalWallet` that holds ERC20 balances of tokens other than the ones referenced in the signed `ops`/`erc20TokenAddresses`. This is realistically reachable by a malicious or compromised relay operator processing a legitimately signed Emporium request, since `feeStructure` is never covered by the wallet owner's EIP-712 hash.

### Recommendation
Add `feeStructure.feeToken` (and ideally `feeStructure.flatFee`/`variableRate`) to the `EMPORIUM_SIGNATURE_TYPEHASH` payload that the wallet owner signs, so `verifyWallet` cryptographically binds the exact fee token and amount cap the signer approved, not just an unscoped numeric `maxFee`.

### Proof of Concept
1. Wallet owner signs an `EmporiumSignature` for `ops = [swap USDC→ETH via router]`, `maxFee = 10 (in USDC)`, `deadline`, `emporiumMessage = N`.
2. A relay/prover assembling the on-chain call builds `circomData` with `feeStructure = {feeToken: DAI, flatFee: 10}` and `erc20TokenAddresses` that do not include `DAI` (so `foundToken = false`), while keeping the same signed `ops`/`maxFee`/`deadline`/`emporiumMessage`.
3. `verifyWallet` passes (`flatFee(10) <= maxFee(10)`); `payRelayFees`'s fallback branch calls `payRelay(relay, signerAddress, 10, DAI)`.
4. `sendToRelayFromWallet` → `HinkalWallet(signerAddress).doSendToRelay(relay, 10, DAI)` transfers 10 DAI from the wallet to the relay — a token/amount pairing the wallet owner never signed for, even though the numeric cap check passed.

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

**File:** contracts/Transferer.sol (L178-190)
```text
    function sendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) internal {
        if (relay != address(0) && actualAmount > 0) {
            transferERC20TokenOrETH(
                erc20TokenAddress,
                relay,
                uint256(actualAmount)
            );
        }
    }
```
