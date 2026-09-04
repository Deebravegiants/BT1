Confirmed: `onlyAllowedRecipient` in `contracts/external-actions/ExternalActionBaseUpgradeable.sol:39-46` only restricts *who can call* `runAction` (i.e., the Hinkal core contract), not what `endpoint`/`callData` an op inside `EmporiumStack.ops` targets. Nothing in `EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-118`) restricts or namespaces the CASE 2 stateless calls (`op.endpoint.call{value: op.value}(op.callData)`) by originating user — the Emporium contract's own address is used as `msg.sender` toward any external protocol for every Hinkal user.

### Title
Cross-user asset theft via shared Emporium identity in stateless (CASE 2) `runAction` calls to external stream/vesting protocols - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When a user creates an external position (e.g., a Sablier-like stream) through `EmporiumUpgradeable.runAction`'s stateless path (`op.invokeWallet == false`, `stack.signerAddress == address(0)`), the call is executed with `msg.sender == EmporiumUpgradeable` itself, since Emporium acts as one shared identity for all Hinkal users on that external protocol [1](#0-0) . Any unrelated Hinkal user can subsequently craft their own `CircomData`/`EmporiumStack` with an op that calls the external protocol's withdrawal function on that same stream/position and redirect the proceeds to themselves, because the external protocol's authorization is keyed to `msg.sender == Emporium address`, which is identical for every caller, not to the specific victim who created the stream.

### Finding Description
The broken equality: `stream.recipient (as tracked by the external protocol, i.e. address(Emporium)) == the specific Hinkal user who deposited into and owns that stream`. This equality does not hold — the external protocol only ever sees one identity, `address(Emporium)`, for CASE 2 ops.

Path: victim calls Hinkal → `_externalTransact` → `EmporiumUpgradeable.runAction` [2](#0-1) , with `EmporiumStack.signerAddress == address(0)` and an op whose `callData` calls `createStream(...)` on a Sablier-like contract with `sender/recipient` set to `address(this)` (Emporium) or left to default to `msg.sender` at the external protocol. The call executes as `op.endpoint.call(op.callData)` from Emporium's own context [3](#0-2) . No `streamId`-to-`originalSender` binding is recorded anywhere on-chain in Hinkal/Emporium.

Attacker's call: after cliff, attacker (any unprivileged EOA who can generate their own valid proof/UTXO and call Hinkal like anyone else) submits their own transaction to Hinkal with `externalActionData.externalAddress = Emporium`, `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and an op calling the same external protocol's `withdraw(streamId, ..., to=attacker)`. Because `msg.sender` at the external protocol is again `address(Emporium)` — the same address that created the stream — the external protocol's permission check passes exactly as it would for the original victim. `handleOut` then pays out the withdrawn balance change to `msg.sender` (Hinkal), and mints a new UTXO under the *attacker's* `stealthAddressStructure`, giving the attacker a valid shielded UTXO for tokens that belonged to the victim's stream [4](#0-3) .

Existing guards do not prevent this: `verifyWallet`'s EIP-712 signature check only applies when `stack.signerAddress != address(0)` (CASE 1, per-user `HinkalWallet`) [5](#0-4) ; CASE 2 has no such per-user binding at all. `usedMessages`/`emporiumMessage` only prevents replay of the *same* message, not an attacker crafting a *new*, independently valid message targeting someone else's external position. `onlyAllowedRecipient` only gates who may call `runAction` (Hinkal core), not what the op targets [6](#0-5) . `dimensionsCheck`, nullifier/root checks, and the circuit's `inTotal + amountChanges === outTotal` constraint only ensure the *proof's own* accounting is internally consistent for the *caller's own* nullifiers/UTXOs — they never constrain which external stream/position ID the op's `callData` is allowed to reference, since `externalActionMetadata`/`callData` bytes are fully attacker-chosen and not tied to circuit signals identifying stream ownership.

### Impact Explanation
An attacker who discovers (e.g., from external protocol events, which are public) a `streamId`/position created via Emporium's CASE 2 path can steal the entire streamed/vested balance belonging to another Hinkal user by withdrawing it into their own shielded UTXO. This is direct theft of another user's funds that were legitimately deposited and held externally through Hinkal's own contract identity — this qualifies as Critical (direct theft of user funds) rather than High, since the victim's assets leave Hinkal-custodied value into the attacker's exclusive control with no recovery path, going beyond mere unauthorized action execution.

### Likelihood Explanation
Preconditions: a victim must have used the Emporium CASE 2 (stateless, `signerAddress = address(0)`) path to interact with an external stream/vesting contract whose withdrawal authorization is based on `msg.sender` rather than an argument-supplied unique owner identity per stream that Hinkal itself enforces. Attacker cost is a single Hinkal transaction with a self-generated valid proof (no special privilege needed) plus knowledge of the `streamId`, which is typically emitted in a public event by the external protocol at creation time. This is fully repeatable for every stream created via the stateless path, for every external protocol whose authorization model is per-`msg.sender` rather than per-argument owner.

### Recommendation
For CASE 2 (stateless) ops, either: (1) disallow stateless interactions with any external protocol that grants withdrawal rights based on `msg.sender` identity (only allow stateless ops for actions where the shared identity poses no risk, e.g., swaps where output is immediately swept out in the same transaction), or (2) require that any external position created through Emporium be created via the CASE 1 per-user `HinkalWallet` path (`invokeWallet = true`) so that the external protocol's owner-tracking is bound to a wallet address unique to the depositing user and any later withdrawal requires that user's EIP-712 signature (as already enforced by `verifyWallet`). Enforce this at the protocol/allowlist level by whitelisting only endpoint+selector combinations known to be safe for stateless (shared-identity) execution, and route anything that creates persistent external positions (streams, vesting, lending positions, staked balances) exclusively through the signed, per-wallet CASE 1 path.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a mock Sablier-like `MockStream` contract with `createStream(address recipient, uint256 amount, uint256 cliff, uint256 duration)` and `withdraw(uint256 streamId, address to, uint256 amount)` that checks `msg.sender == stream.sender` only (no per-caller sub-identity).
2. Victim: submit Hinkal transaction with `CircomData.externalActionData.externalAddress = Emporium`, metadata encoding `EmporiumStack{signerAddress: address(0), ops: [{endpoint: MockStream, invokeWallet: false, callData: createStream(address(Emporium), amount, cliff, duration)}]}`. Assert stream created with `sender == address(Emporium)`.
3. `vm.warp` past cliff.
4. Attacker: submit a separate Hinkal transaction (attacker's own valid proof/UTXOs, different `emporiumMessage`) with `EmporiumStack{signerAddress: address(0), ops: [{endpoint: MockStream, invokeWallet: false, callData: withdraw(streamId, attackerAddress, streamedAmount)}]}`.
5. Assert: `token.balanceOf(attackerAddress or attacker's new UTXO commitment)` increases by `streamedAmount`, and the victim's ability to later withdraw the same funds fails/reverts (funds already drained) — proving `stream owner (Emporium, shared) != victim`, i.e., the claimed equality is broken and attacker receives victim's streamed tokens.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L97-118)
```text
            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
            }
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }

            if (!success) {
                revert CallFailed(err);
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
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

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```
