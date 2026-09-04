### Title
Emporium "min" path (`erc20TokenAddresses.length == 0`) lets an unprivileged EOA drain arbitrary ERC20/ETH balances held by `EmporiumUpgradeable` with an unconstrained proof and zero balance verification - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`, `contracts/CircomDataBuilder.sol`, `circuits/MainEVMCircuitMin.circom`)

### Summary
The external report's core bug class is that a low-level call-forwarding mechanism (`MsgValueSimulator`→`mimicCall`) allowed the `to`/`value` of a forwarded call to be corrupted, letting a contract's own funds move to an unintended destination *without the balance/authorization accounting ever detecting it*. The direct analog in Hinkal is `EmporiumUpgradeable.runAction()`'s arbitrary op-execution loop (`op.endpoint.call{value: op.value}(op.callData)`), combined with the "Emporium min" code path, where the balance-conservation check that is supposed to bound what those forwarded calls can move is entirely skipped, and the ZK proof that is supposed to authorize the operation carries **no spending/ownership constraints at all**.

### Finding Description
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes the public-input construction to `formInputEmporiumMin`, which only emits `emporiumMessage`, `timeStamp`, and `calldataHash` as public signals: [1](#0-0) 

The corresponding circuit, `MainEVMCircuitMin`, contains **no nullifier check, no Merkle-root check, no signature verification, and no balance-conservation constraint** — it only computes `message <== Poseidon(1)([messageSeed])` and exposes `outTimeStamp`/`calldataHash`: [2](#0-1) 

Because `circomData.erc20TokenAddresses` is empty in this path, `Hinkal.transact()`'s balance-equation loop (which normally enforces `balanceDif == amountChanges[i] + utxoAmount`) iterates zero times and enforces nothing: [3](#0-2) 

`_externalTransact` similarly has an empty `deltaAmountChanges` array and transfers nothing from Hinkal before invoking the external action: [4](#0-3) 

Inside `EmporiumUpgradeable.runAction`, `getBalancesForArray(circomData.erc20TokenAddresses)` before/after is likewise a no-op for an empty array, so the post-condition checks (`BalanceChangeShouldBePositive`, `handleOut`) never execute for any token: [5](#0-4) 

Meanwhile the operation loop unconditionally executes attacker-supplied `EmporiumOperation`s. When `stack.signerAddress == address(0)` (the "stateless"/self-authorized case), `verifyWallet` skips ECDSA signature verification entirely and merely marks the message as used: [6](#0-5) 

In that case, CASE 2 ("Stateless Interaction") calls `op.endpoint.call{value: op.value}(op.callData)` with attacker-chosen `endpoint`, `value`, and `callData` (only the `callHinkalWallet`/`doSendToRelay` selectors are blocked): [7](#0-6) 

`EmporiumUpgradeable` also has a permissive `receive()` that accepts ETH from anyone, and, being the destination that Hinkal sends withdrawal amounts to and the temporary holder of relay fees / swap residues / other users' in-flight funds, can accumulate ETH/ERC20 balance across transactions: [8](#0-7) 

Putting this together: an unprivileged EOA can call `Hinkal.transact()` with `circomData.erc20TokenAddresses = []`, `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and one or more `ops` targeting any ERC20 token contract (`transfer(attacker, balance)`) or plain ETH transfer to themselves, and a trivial Groth16 proof for `MainEVMCircuitMin` (which only needs `message == Poseidon(messageSeed)` — no ownership of any shielded UTXO is required). `HinkalHelper.performHinkalChecks` only re-derives `calldataHash` and checks dimensions match `erc20TokenAddresses.length == 0`; it never ties the arbitrary `ops` to any real balance movement: [9](#0-8) 

This breaks the equality the balance-conservation logic is meant to enforce (`balanceDif == amountChanges + utxoAmount`, checked per `erc20TokenAddresses[i]`), because the value moved by the external action (via arbitrary `op.endpoint.call`) is never included in `erc20TokenAddresses`, hence never checked — exactly the "value moved but not counted in the balance equation" analog to the register-corruption bug where the simulated call's `to`/`value` bypassed the caller's own accounting.

### Impact Explanation
Any funds sitting in `EmporiumUpgradeable` (relay/protocol fees routed through it, ETH/ERC20 residue from swaps or partially-executed prior operations, or other users' funds mid-flight during a batched/relayed operation) can be siphoned to an attacker with no signature, no nullifier spend, and no proof of legitimate ownership — this is a Critical-severity proof/nullifier-verification bypass leading to direct theft of protocol/relay fees and any pooled funds in Emporium, and could also be used to reach `Critical` if Emporium ever custodies user shielded value in transit.

### Likelihood Explanation
High. The attack requires only a normal user-controlled call to `Hinkal.transact()` with a self-generated Groth16 proof for the intentionally trivial `MainEVMCircuitMin`/`formInputEmporiumMin` path, and crafting `EmporiumOperation[]` data — no admin, relay, or other user's key is needed, and the `signerAddress == address(0)` branch is a documented/first-class code path (not a corner case), making exploitation straightforward for any unprivileged EOA.

### Recommendation
- Require `erc20TokenAddresses`/`amountChanges` (or an equivalent explicit token allow-list bound into `calldataHash`/circuit constraints) to cover every token/ETH balance touched by `EmporiumOperation.endpoint` calls, and enforce the balance-conservation check over that full set even in the "Emporium min" path.
- Do not allow a fully unconstrained circuit (`MainEVMCircuitMin`) to authorize arbitrary `call{value}` operations; at minimum bind the op list and target balances into signals that are checked against actual pre/post balances for every token moved, not just the declared `erc20TokenAddresses`.
- Reconsider allowing `stack.signerAddress == address(0)` to skip ECDSA verification while still permitting arbitrary `endpoint`/`value`/`callData`; if this "stateless" mode is intended for self-authorized proof-only flows, the proof must actually constrain the balance change of every token the ops can touch.

### Proof of Concept
1. Attacker (any EOA, no shielded balance required) builds `circomData` with:
   - `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `slippageValues = []`, `inputNullifiers = []`, `outCommitments = []` (all consistent with `dimensions.tokenNumber = 0`).
   - `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress = <Emporium address>`.
   - `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{ signerAddress: address(0), ops: [EmporiumOperation{ endpoint: <ERC20 held by Emporium>, invokeWallet: false, value: 0, callData: transfer(attacker, balanceOfEmporium) }] })`.
2. Attacker generates a Groth16 proof for `MainEVMCircuitMin`, choosing any `messageSeed` such that `message == Poseidon(messageSeed)` — trivially satisfiable, no knowledge of any UTXO/private key needed.
3. Attacker calls `Hinkal.transact(a, b, c, dimensions, circomData)`.
   - `performHinkalChecks` only validates `calldataHash` and dimension lengths (all zero) — passes.
   - `verifyProof` succeeds against the trivial circuit.
   - `_externalTransact` transfers nothing (empty token array) and calls `EmporiumUpgradeable.runAction`.
   - `verifyWallet` skips signature check because `signerAddress == address(0)`.
   - The op loop executes `token.call(transfer(attacker, balance))`, draining the token from Emporium.
   - `balancesBefore`/`balancesAfter` loop is over the empty `erc20TokenAddresses`, so no revert occurs despite Emporium's balance for that token dropping to zero.
4. Result: attacker has moved value out of `EmporiumUpgradeable` that is never checked against the balance-conservation invariant, and required no signature or shielded funds ownership whatsoever.

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

**File:** circuits/MainEVMCircuitMin.circom (L1-18)
```text

pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

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

**File:** contracts/Hinkal.sol (L76-147)
```text
            UTXO[] memory utxoSet;

            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-370)
```text
    receive() external payable {}
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
