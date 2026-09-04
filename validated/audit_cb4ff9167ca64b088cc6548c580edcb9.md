### Title
Emporium `runAction` allows unauthenticated arbitrary calls with zero balance accounting via `signerAddress == 0` + empty `erc20TokenAddresses` (Min-proof path) - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`CircomDataBuilder.formInputForCircom` routes any transaction with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0` to `formInputEmporiumMin`, a proof that only attests knowledge of `Poseidon(messageSeed)`. In `EmporiumUpgradeable.runAction`, when the attacker-controlled `EmporiumStack.signerAddress == address(0)`, `verifyWallet` skips all EIP-712 signature verification, and the balance-accounting loop iterates over the (empty) `erc20TokenAddresses` array, so arbitrary `stack.ops` calls dispatched with Emporium's own identity are neither authenticated nor accounted for.

### Finding Description
The invariant that should hold is: *every asset movement Emporium's `ops` loop can perform must be captured by the `balancesBefore`/`balancesAfter` diff over `circomData.erc20TokenAddresses`.* This equality is broken because the two loops are bounded by independent, both attacker-controlled, lengths:

- The ops-execution loop is bounded by `stack.ops.length` [1](#0-0) .
- The accounting loop is bounded by `circomData.erc20TokenAddresses.length` [2](#0-1) .

When `circomData.erc20TokenAddresses.length == 0`, `formInputForCircom` selects the minimal proof `formInputEmporiumMin`, which only asserts `message == Poseidon(messageSeed)`, `timeStamp`, and `calldataHash` — no nullifiers, no root inclusion of UTXOs, no in/out totals: [3](#0-2) . This is a legitimately registered configuration (`mainEVMCircuitMin0v4` verifier keyed by `buildVerifierId(dimensions, externalActionId)` with `tokenNumber == 0`) [4](#0-3) , and `dimensionsCheck` only requires `erc20TokenAddresses.length == dimensions.tokenNumber`, which the attacker sets to `0` themselves [5](#0-4) .

Separately, `verifyWallet` is the sole gate on what `stack.ops` may do. When `stack.signerAddress == address(0)`, it marks `emporiumMessage` used and returns immediately — no EIP-712 signature, no deadline, no fee-cap check: [6](#0-5) . The attacker freely chooses `emporiumMessage` and a `messageSeed` such that `Poseidon(messageSeed) == emporiumMessage`, satisfying the Min circuit trivially.

Exploit flow:
1. Attacker calls `Hinkal.transact` with `dimensions.tokenNumber = 0`, `circomData.erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress` = the registered Emporium contract, and `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [<arbitrary call>], ...})`.
2. `performHinkalChecks` passes (`dimensionsCheck`, `checkOnchainCreation` are no-ops for empty arrays), `formInputForCircom` builds the trivial Min input, and the Min proof verifies [7](#0-6) .
3. `Hinkal._externalTransact` iterates zero tokens (no pre-transfer) then calls `EmporiumUpgradeable.runAction` [8](#0-7) .
4. `runAction` snapshots `balancesBefore` for zero tokens, `verifyWallet` no-ops due to `signerAddress == 0`, then the ops loop executes `op.endpoint.call{value: op.value}(op.callData)` as `EmporiumUpgradeable` itself (Case 2, stateless) [9](#0-8) . The only restriction is that the call's selector isn't `callHinkalWallet`/`doSendToRelay`; the target and calldata are otherwise unconstrained, so the attacker can, e.g., call `token.transfer(attacker, EmporiumBalance)` for any token Emporium holds.
5. The post-loop accounting loop is empty (zero tokens), so nothing reverts, and no leftover UTXO is created for the drained token — the theft is invisible to Hinkal's own bookkeeping.

Existing guards fail specifically because: `dimensionsCheck`/`checkOnchainCreation` only validate array-length consistency, not that the listed tokens cover everything `ops` might touch; the circuit's Min variant intentionally constrains almost nothing; and `verifyWallet`'s authorization is entirely conditioned on `signerAddress != 0`, which is attacker-selectable.

### Impact Explanation
Any value sitting in the `EmporiumUpgradeable` contract's own balance (ETH or ERC-20) — whether from protocol fee remnants, rounding dust, unlisted intermediate tokens from prior multi-op transactions, reward/airdrop tokens accrued from `ops`-initiated positions, or mistaken direct transfers — can be swept by an unprivileged caller with a single, cheap-to-produce Min proof and zero signature. This is direct theft of protocol/relay-held (and potentially in-flight user) funds, matching the Critical impact category (direct theft of shielded or in-flight user funds). The attack is repeatable every block, limited only by `usedMessages[emporiumMessage]` uniqueness, which the attacker trivially avoids by choosing a fresh `messageSeed` each time.

### Likelihood Explanation
Preconditions: Emporium must be registered as `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]` (already required for the feature to function at all) and must hold some balance to drain, which accumulates naturally over protocol operation. The attacker needs no special role — any EOA can call `Hinkal.transact`, generate the trivial Min proof locally, and craft the `EmporiumStack`/`EmporiumOperation` calldata. Cost is a single transaction's gas. This is highly feasible and repeatable.

### Recommendation
- Require `stack.signerAddress != address(0)` (i.e., mandatory EIP-712 authorization) whenever `stack.ops` contains any Case-2 (stateless) operation that isn't purely deposit-related, or otherwise disallow the Min proof path (`erc20TokenAddresses.length == 0`) from being combined with a non-empty `ops` array.
- Make the balance-accounting loop track every token/asset actually touched by `stack.ops` (not just `circomData.erc20TokenAddresses`), or require `erc20TokenAddresses` to be a superset of all addresses/tokens referenced by `ops`, verified on-chain.
- Alternatively, restrict the Min-proof path to a fixed, non-arbitrary action set that cannot invoke `op.endpoint.call` with attacker-controlled target/data at all.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (proxy), register Emporium under `HINKAL_EMPORIUM_ACTION_ID`, register the `mainEVMCircuitMin0v4` verifier for `buildVerifierId({tokenNumber:0,nullifierAmount:0,outputAmount:0}, HINKAL_EMPORIUM_ACTION_ID)`.
2. Fund `EmporiumUpgradeable` directly with e.g. 1000 `MockERC20` tokens (simulating "parked"/leftover balance) — `assertEq(token.balanceOf(emporium), 1000e18)`.
3. Attacker (non-owner EOA) builds `CircomData` with `erc20TokenAddresses = []`, `dimensions.tokenNumber = 0`, `externalActionData = {externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalAddress: emporium, externalActionMetadata: abi.encode(EmporiumStack({v:0,r:0,s:0, signerAddress: address(0), ops: [EmporiumOperation({endpoint: address(token), invokeWallet: false, value: 0, callData: abi.encodeCall(token.transfer, (attacker, 1000e18))})], maxFee: 0, deadline: 0}))}`.
4. Generate `messageSeed`, compute `emporiumMessage = Poseidon(messageSeed)` off-chain (snarkjs), produce Groth16 proof `(a,b,c)` for `MainEVMCircuitMin` with public inputs `[emporiumMessage, timeStamp, calldataHash]`.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from attacker's EOA.
6. Assert: tx succeeds, `token.balanceOf(attacker) == 1000e18` after, `token.balanceOf(emporium) == 0` after — proving the balance-accounting equality (`balancesBefore == balancesAfter` for the empty tracked-token set) was violated relative to the real asset movement, with no revert and no signature ever checked.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
        for (uint256 i = 0; i < stack.ops.length; i++) {
            EmporiumOperation memory op = stack.ops[i];

            bool success;
            bytes memory err;

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-151)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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

**File:** contracts/CircomDataBuilder.sol (L134-161)
```text
    function formInputForCircom(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory) {
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }

    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }
```

**File:** contracts/VerifierFacade.sol (L28-43)
```text
    function buildVerifierId(
        Dimensions calldata dimensions,
        uint256 externalActionId
    ) public pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        dimensions.tokenNumber,
                        dimensions.nullifierAmount,
                        dimensions.outputAmount,
                        externalActionId
                    )
                )
            );
    }
```

**File:** contracts/HinkalHelper.sol (L64-75)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );
```

**File:** contracts/Hinkal.sol (L36-65)
```text
    ) public payable nonReentrant {
        {
            uint256[] memory inputForCircom = hinkalHelper.performHinkalChecks(
                circomData,
                dimensions,
                msg.sender
            );

            require(
                verifyProof(
                    a,
                    b,
                    c,
                    inputForCircom,
                    buildVerifierId(
                        dimensions,
                        circomData.externalActionData.externalActionId
                    )
                ),
                "Invalid Proof"
            );
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
        }
```

**File:** contracts/Hinkal.sol (L244-261)
```text
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
