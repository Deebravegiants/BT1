## Analysis

The equality being tested is: **assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`** (and in `Hinkal.sol`'s own `oldBalances`/`newBalances` reconciliation loop). Tracing the code shows this equality is broken whenever `circomData.erc20TokenAddresses.length == 0`.

**Path:**
1. `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`. [1](#0-0) 

2. `MainEVMCircuitMin` only constrains `message === Poseidon(messageSeed)`; `outTimeStamp` and `calldataHash` are declared public inputs but never appear in any constraint, so any prover can generate a single valid Min proof and reuse it with arbitrary `calldataHash`/`timeStamp` values at verification time (unconstrained public signals do not affect the Groth16 pairing check). [2](#0-1) 

3. `HinkalHelper.performHinkalChecks` only checks internal self-consistency of `calldataHash` against the supplied fields (`getHashedCalldata`) — not against anything provably tied to the proof itself — and `dimensionsCheck`/`checkOnchainCreation` trivially pass with zero-length arrays. [3](#0-2) [4](#0-3) 

4. `Hinkal.transact`'s balance-accounting loop (the "balance equation") iterates only `circomData.erc20TokenAddresses.length` times, so with an empty array **the entire slippage/balance-diff/onChainCreation invariant is skipped completely**, not merely weakened. [5](#0-4) 

5. `EmporiumUpgradeable.runAction` decodes an attacker-controlled `EmporiumStack` from `externalActionData.externalActionMetadata`. With `signerAddress == address(0)`, `verifyWallet` performs no signature check at all (only marks the message used) and each `op` in `stack.ops` is executed as `op.endpoint.call{value: op.value}(op.callData)` — a raw, unrestricted external call made with `msg.sender == EmporiumUpgradeable` (i.e., from the Emporium's own identity/asset custody). [6](#0-5) [7](#0-6) 

6. `runAction`'s own reconciliation loop (`balancesBefore`/`balancesAfter`) is also computed strictly over `circomData.erc20TokenAddresses`, which the attacker forced to be empty — so any token the malicious `op` actually moves (e.g., `IERC20(target).transfer(attacker, balance)`) is invisible to both this loop and Hinkal's outer loop. [8](#0-7) 

This confirms the attack: an unprivileged actor calls `Hinkal.transact` with `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, an empty `erc20TokenAddresses`/`amountChanges`/`onChainCreation` set (all dimension checks pass trivially at 0), a locally-generated Min proof (no real secret required — `messageSeed` is self-chosen), and an `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress == address(0)` whose single op calls `erc20.transfer(attacker, balance)` on any token the Emporium contract holds. No check anywhere in `Hinkal.sol`, `HinkalHelper.sol`, or `EmporiumUpgradeable.sol` catches the resulting balance change, because every accounting loop is keyed to the (empty) declared token list rather than to what the op actually touched.

### Title
Empty-token Emporium Min-proof path allows unaccounted arbitrary calls draining Emporium-held ERC20 balances - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol, contracts/CircomDataBuilder.sol, contracts/Hinkal.sol)

### Summary
Setting `externalActionId == HINKAL_EMPORIUM_ACTION_ID` with `erc20TokenAddresses.length == 0` routes proof-input generation to `formInputEmporiumMin`, which only proves `message == Poseidon(messageSeed)` — a trivially self-satisfiable statement requiring no ownership of any UTXO. Because both `EmporiumUpgradeable.runAction`'s balance loop and `Hinkal.transact`'s outer balance/slippage loop iterate strictly over `circomData.erc20TokenAddresses`, an empty array makes all balance accounting a no-op, while the attacker-supplied `EmporiumStack` can still execute an arbitrary, unsigned (`signerAddress == 0`) external call from Emporium's own identity, moving any ERC20 tokens the Emporium contract holds to the attacker.

### Finding Description
The broken equality: *assets Emporium moves in a transaction == assets accounted for in `balancesBefore`/`balancesAfter` and `oldBalances`/`newBalances`*. This holds only when `erc20TokenAddresses` lists every token an op could touch. By choosing `erc20TokenAddresses = []` to force the Min-circuit path (`formInputForCircom` in `contracts/CircomDataBuilder.sol:139-148`), the attacker makes both `getBalancesForArray(circomData.erc20TokenAddresses)` calls in `EmporiumUpgradeable.runAction` (lines 85, 122) operate on an empty set, and makes `Hinkal.transact`'s reconciliation loop (`contracts/Hinkal.sol:97-146`) execute zero iterations. Meanwhile, `stack.ops` (fully attacker-controlled via `externalActionMetadata`) is executed unconditionally via `op.endpoint.call{value: op.value}(op.callData)` when `signerAddress == address(0)` (`EmporiumUpgradeable.sol:102-113`), with no signature requirement (`verifyWallet` returns immediately for `signerAddress == address(0)`, `EmporiumUpgradeable.sol:314-316`). This call executes with `msg.sender == EmporiumUpgradeable`, so a call like `erc20.transfer(attacker, erc20.balanceOf(address(this)))` transfers out any token balance Emporium currently custodies, with zero downstream check detecting the movement. The `calldataHash` and `emporiumMessage` public signals passed into the Min circuit are unconstrained by `MainEVMCircuitMin` (only `message = Poseidon(messageSeed)` is constrained), so the attacker can also freely rebind a proof to any `externalActionMetadata`/`calldataHash` combination satisfying only `HinkalHelper.performHinkalChecks`'s self-consistency hash check, not any cryptographic commitment enforced by the circuit itself.

### Impact Explanation
Any ERC20 or native-token balance held by the `EmporiumUpgradeable` contract at the time of the attack (e.g., from partially-processed flows, dust, fee remainders, or any legitimate deposit-in-progress) can be directly stolen by an unprivileged caller with no signature or ownership proof. This matches Critical: direct theft of shielded or in-flight user funds, and separately, "executing calls...a wallet owner or prover never authorised," since the attacker's op runs from Emporium's identity without any signer authorization. The attack is repeatable on every transaction as long as Emporium holds a positive balance of some token.

### Likelihood Explanation
Preconditions: Emporium contract must hold a nonzero balance of some ERC20/ETH at attack time (plausible given `receive() external payable {}` and the transient in/out balance flows of the stateless op path). Attacker cost is a single transaction plus generating one Min-circuit proof off-chain (trivial, since `messageSeed` is self-chosen and no real secret/UTXO ownership is required). No privileged role or relay is needed since the attacker can set `relay == address(0)` and `originalSender == msg.sender` per `performHinkalChecks`'s originalSender branch. This is fully attacker-triggerable and repeatable.

### Recommendation
Do not allow the Emporium action to bypass balance accounting via an empty `erc20TokenAddresses` array. Either (a) forbid `HINKAL_EMPORIUM_ACTION_ID` combined with a zero-length token array from selecting a proof path that skips balance checks, (b) enforce `EmporiumUpgradeable.runAction`'s and `Hinkal.transact`'s balance reconciliation independent of the declared `erc20TokenAddresses` (e.g., snapshot/diff over the actual set of tokens touched by `stack.ops`, or require every `op.endpoint` be declared in `erc20TokenAddresses`), or (c) properly constrain `calldataHash`/`outTimeStamp`/all metadata fields inside the Min circuit itself so the proof cryptographically binds to one specific, non-replayable `externalActionMetadata`.

### Proof of Concept
Foundry plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium as allowed external action.
2. Fund `EmporiumUpgradeable` directly with `TOKEN.transfer(emporium, 1000e18)` to simulate residual/in-flight balance.
3. Generate a Min-circuit proof off-chain for an arbitrary `messageSeed` (no ownership required) using the `MainEVMCircuitMin` artifacts.
4. Craft `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: address(TOKEN), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e18))}]})`.
5. Call `Hinkal.transact(a, b, c, dimensions{tokenNumber:0,...}, circomData)` from attacker EOA.
6. Assert: `TOKEN.balanceOf(attacker)` increases by `1000e18`; `TOKEN.balanceOf(emporium)` goes to 0; transaction does not revert despite no balance being declared/accounted in `circomData.erc20TokenAddresses`.

### Citations

**File:** contracts/CircomDataBuilder.sol (L139-161)
```text
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

**File:** circuits/MainEVMCircuitMin.circom (L6-18)
```text
template MainEVMCircuitMin() {
  // Public inputs:
  signal input outTimeStamp;
  signal input calldataHash;

  // Private inputs:
  signal input messageSeed;

  // outputs:
  signal output message;

  message <== Poseidon(1)([messageSeed]);
}
```

**File:** contracts/HinkalHelper.sol (L180-200)
```text
        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
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

**File:** contracts/Hinkal.sol (L97-146)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-151)
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
