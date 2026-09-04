### Title
Emporium Min-circuit path lets any unprivileged caller drain Emporium's ERC20/ETH balances via unauthenticated ops with zero balance accounting - (File: `contracts/CircomDataBuilder.sol`, `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`, `contracts/Hinkal.sol`)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only proves `emporiumMessage == Poseidon(messageSeed)` and never constrains the `EmporiumStack` ops. Combined with `EmporiumUpgradeable.verifyWallet` skipping signature verification whenever `stack.signerAddress == address(0)`, and both `Hinkal.transact`'s and `EmporiumUpgradeable.runAction`'s balance-accounting loops being bounded by the attacker-chosen empty `erc20TokenAddresses` array, an attacker can execute arbitrary `op.endpoint.call{value: op.value}(op.callData)` from Emporium's identity and move any ERC20/ETH balance Emporium holds to themselves with no accounting, no signature, and no proof constraint on the operations performed.

### Finding Description
The broken equality is: *assets Emporium's `runAction` is allowed to move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter` and in `Hinkal.transact`'s balance-diff loop*.

Path:
1. `formInputForCircom` selects the minimal circuit whenever `erc20TokenAddresses.length == 0` for the Emporium action id: [1](#0-0) 
`formInputEmporiumMin` only feeds `emporiumMessage`, `timeStamp`, `calldataHash` as public signals — it never constrains `externalActionMetadata` (the `EmporiumStack`), `erc20TokenAddresses`, or `amountChanges` inside the proof itself.

2. `Hinkal.transact` calls `hinkalHelper.performHinkalChecks`, which only checks `getHashedCalldata(circomData) == circomData.calldataHash` (a plain equality the attacker trivially satisfies since they construct both sides themselves) and `dimensionsCheck`/`checkOnchainCreation`, none of which validate the *content* of `EmporiumStack` ops: [2](#0-1) 

3. `Hinkal.transact`'s post-action balance-difference/slippage loop is bounded by `circomData.erc20TokenAddresses.length`, which is attacker-controlled and set to 0, so the loop never executes and never checks any real balance movement: [3](#0-2) 

4. `_externalTransact` builds `deltaAmountChanges` sized to `erc20TokenAddresses.length` (0), pulls nothing from the attacker, and calls `IExternalActionV2(...).runAction`: [4](#0-3) 

5. In `EmporiumUpgradeable.runAction`, `balancesBefore`/`balancesAfter` are also computed over the same empty `circomData.erc20TokenAddresses`, so they capture nothing: [5](#0-4) 

6. `verifyWallet` skips ALL signature verification when `stack.signerAddress == address(0)`: [6](#0-5) 

7. With `signerAddress == address(0)`, every op falls into "CASE 2: Stateless Interaction" and is executed as `op.endpoint.call{value: op.value}(op.callData)` directly from Emporium's own address, e.g. calling `token.transfer(attacker, EmporiumBalance)` on any token Emporium currently holds (deposited by any user through the normal path, or ETH sent to Emporium's `receive()`): [7](#0-6) [8](#0-7) 

8. Back in `runAction`, the final `utxoSet`-building loop is again bounded by the empty `erc20TokenAddresses` array, so `utxoSetLength` stays 0 and an empty `utxoSet` is returned regardless of the stolen tokens: [9](#0-8) 

The attacker's call is `Hinkal.transact(a, b, c, dimensions, circomData)` where `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `circomData.erc20TokenAddresses == []`, `circomData.externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [transfer-to-attacker op]})`, and `emporiumMessage = Poseidon(messageSeed)` for a seed the attacker knows (self-chosen, requires no victim cooperation).

Existing guards that fail to prevent this:
- `dimensionsCheck`/`checkOnchainCreation` only validate array-length consistency across attacker-supplied, empty arrays — they never bound what `EmporiumStack.ops` can do.
- `calldataHash` equality check is a hash-of-attacker-supplied-data-equals-attacker-supplied-hash check, not an authorization control.
- `verifyProof` on the min circuit only proves knowledge of a Poseidon preimage the attacker picks themselves; it does not bind or constrain the ops.
- `rootHashExists`/nullifier checks are irrelevant since no UTXOs are spent (`inputNullifiers` dimensioned to 0 tokens).

### Impact Explanation
An unprivileged attacker can steal any ERC20 token balance or ETH balance currently held by the `EmporiumUpgradeable` contract (which legitimately accrues balances from any user's normal Emporium deposit flow, or dust/leftover balances between operations), by issuing a single `Hinkal.transact` call with a trivial self-generated proof and no signature. This is direct theft of shielded/in-flight funds belonging to other Hinkal users or the protocol, matching the Critical severity category "direct theft of shielded or in-flight user funds." The attack is repeatable for any balance Emporium accumulates over time and costs the attacker only gas plus proof-generation for the min circuit.

### Likelihood Explanation
Preconditions: `erc20TokenAddresses.length == 0` and Emporium action id must be reachable via `formInputForCircom`, both fully attacker-controlled; `EmporiumStack.signerAddress == address(0)` is also fully attacker-controlled and bypasses signature checks entirely; Emporium must hold a nonzero balance in some token/ETH at call time (a realistic and common state given normal deposit flows go through Emporium's balance). No relayer, admin, or victim cooperation is required — the attacker only needs to be able to call `Hinkal.transact` with a self-generated min-circuit proof, which the protocol design explicitly supports as a "fast path." This makes the attack highly feasible and repeatable whenever Emporium holds any balance.

### Recommendation
- Do not let `erc20TokenAddresses.length == 0` bypass balance accounting in `EmporiumUpgradeable.runAction`: compute `balancesBefore`/`balancesAfter` (and the corresponding checks in `Hinkal.transact`) over the full set of tokens/ETH actually touched by `stack.ops` (e.g., derived from `op.endpoint`/`op.callData`, or require callers to declare every touched token in `erc20TokenAddresses` and enforce that ops can only touch declared tokens).
- Never allow `stack.signerAddress == address(0)` to fully skip authorization for stateless ops that can move Emporium-held funds; either require the min-circuit proof to fully constrain the encoded `EmporiumStack.ops` (endpoint, callData, value) via `calldataHash`/circuit signals bound in-circuit, or disallow the min-circuit path entirely when `ops` contains calls capable of transferring value/tokens out of Emporium.
- Reject `externalActionMetadata` combinations where `erc20TokenAddresses.length == 0` but `ops` perform state-changing external calls, or require min-path Emporium calls to only cancel/no-op rather than execute arbitrary `ops`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium under `HINKAL_EMPORIUM_ACTION_ID` via `registerExternalAction`.
2. Fund Emporium with `TOKEN.transfer(emporium, 1000e18)` (simulating residual/legit user deposits held in Emporium).
3. Attacker crafts `EmporiumStack{ v,r,s: 0, signerAddress: address(0), ops: [EmporiumOperation{endpoint: TOKEN, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e18))}], maxFee: 0, deadline: type(uint256).max}`.
4. Build `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `slippageValues = []`, `inputNullifiers = []`, `outCommitments = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata = abi.encode(stack)`, `emporiumMessage = Poseidon(seed)` (attacker-chosen `seed`), `calldataHash = getHashedCalldata(circomData)`.
5. Generate a real min-circuit proof (`MainEVMCircuitMin`/`VerifierEVMMin0v4`) proving `emporiumMessage == Poseidon(seed)`.
6. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from attacker EOA.
7. Assert: `TOKEN.balanceOf(emporium)` before == 1000e18, after == 0; `TOKEN.balanceOf(attacker)` after == before + 1000e18; assert `Hinkal.transact` did not revert on any balance/slippage check (loop bound 0 iterations), confirming the equality "assets moved == assets accounted" is violated (1000e18 moved vs. 0 accounted).

### Citations

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

**File:** contracts/Hinkal.sol (L88-147)
```text
            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-130)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

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

        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-159)
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-369)
```text
    receive() external payable {}
```
