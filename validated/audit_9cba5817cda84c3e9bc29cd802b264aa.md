### Title
Empty `erc20TokenAddresses` on Emporium min-circuit path lets an attacker drain Emporium's token balances with zero balance-equation enforcement - (File: contracts/CircomDataBuilder.sol, contracts/Hinkal.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, whose target circuit `MainEVMCircuitMin` only proves knowledge of a self-chosen `messageSeed` and binds `outTimeStamp`/`calldataHash` — it enforces nothing about nullifiers, roots, or token amounts. Because the balance-accounting loops in both `Hinkal.transact` and `EmporiumUpgradeable.runAction` iterate over `circomData.erc20TokenAddresses`, an attacker who submits that array as empty causes both loops to execute zero times, letting arbitrary `stack.ops` calls (e.g., `token.transfer(attacker, allBalance)` executed with `msg.sender == Emporium`) drain real tokens with no balance check anywhere in the call stack.

### Finding Description
The claimed broken equality is: `token.balanceOf(Emporium)_before == token.balanceOf(Emporium)_after + amountChanges + utxoAmount`, which is supposed to be enforced by:
- `Hinkal.transact`'s per-token loop `for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) { ... balanceDif == amountChanges[i] + utxoAmount ... }` [1](#0-0) 
- `EmporiumUpgradeable.runAction`'s per-token loop that computes `balanceChange` and calls `handleOut` to mint a UTXO for any positive delta [2](#0-1) 

Both loops key off `circomData.erc20TokenAddresses`, and this is the *same* calldata struct passed all the way down (`Hinkal.transact` → `_externalTransact` → `IExternalActionV2.runAction`), so setting `erc20TokenAddresses = []` makes **both** loops iterate zero times, and the equality is vacuously "true" over an empty set while real ERC20 movement happens via `stack.ops`.

The attacker's path:
1. `formInputForCircom` picks the min-circuit branch solely on `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` [3](#0-2) .
2. `formInputEmporiumMin` produces only 3 public inputs: `emporiumMessage`, `timeStamp`, `calldataHash` [4](#0-3) .
3. The corresponding circuit `MainEVMCircuitMin` proves nothing except `message == Poseidon(messageSeed)` — no nullifiers, roots, or amount constraints exist at all [5](#0-4) . Any attacker can trivially generate this proof for a self-chosen seed.
4. `performHinkalChecks` only validates calldata-hash integrity, relay validity, `dimensionsCheck` (which just requires arrays to be self-consistently zero-length), and `checkOnchainCreation` — none of which constrain token movement [6](#0-5) .
5. `_externalTransact` builds `deltaAmountChanges` sized to the (empty) `erc20TokenAddresses`, so no funds move into Emporium, then calls `EmporiumUpgradeable.runAction` [7](#0-6) .
6. In `runAction`, `verifyWallet` returns immediately with **no signature check** whenever `stack.signerAddress == address(0)` [8](#0-7) .
7. The stateless-interaction branch executes `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract, blocking only the `callHinkalWallet`/`doSendToRelay` selectors — a plain `IERC20.transfer(attacker, amount)` selector is not blocked [9](#0-8) . This call executes as `token.transfer(attacker, amount)` with `msg.sender == Emporium`, directly draining Emporium's real token balance.
8. Both `balancesBefore`/`balancesAfter` in `runAction` and `oldBalances`/`newBalances` in `Hinkal.transact` are computed over the empty `erc20TokenAddresses` array, so this drain is never detected or blocked by any balance/slippage require.

### Impact Explanation
Direct theft of any ERC20 token balance held by the `Emporium` contract (in-flight/protocol funds belonging to users mid-swap or otherwise custodied by Emporium), executed by an unprivileged attacker with no compromised role. This fully bypasses value conservation across the entire call stack (both `Hinkal.transact`'s balance/slippage checks and `EmporiumUpgradeable.runAction`'s per-token accounting), matching Critical - "direct theft of shielded or in-flight user funds." The attack is repeatable per unique `emporiumMessage` and per token balance available in the Emporium contract.

### Likelihood Explanation
Preconditions are minimal and require no privilege: (1) `Emporium` must already be registered as `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]` and be an allowed recipient of `Hinkal` — both are ordinary deployment configuration, not attacker-controlled privileges, but standard operating state of the protocol; (2) the attacker needs to hold any nonzero ERC20 balance to drain from Emporium (which will exist whenever legitimate users route swaps/transfers through Emporium); (3) the attacker generates a trivial, self-sufficient ZK proof for `MainEVMCircuitMin` requiring no real deposits, nullifiers, or UTXOs; (4) no relay or signature is required since `circomData.relay = address(0)` and `stack.signerAddress = address(0)` are both attacker-choosable. This is fully reachable by any EOA and cheaply repeatable.

### Recommendation
Do not let the balance-accounting/slippage loops in `Hinkal.transact` and `EmporiumUpgradeable.runAction` be sized by the same attacker-controlled `erc20TokenAddresses` array that is empty in the min-circuit path. Either (a) forbid arbitrary `op.endpoint`/`callData` execution when `stack.signerAddress == address(0)` and `erc20TokenAddresses.length == 0` (require min-path Emporium actions to be pure "message" ops that cannot make external calls), or (b) require the min circuit to bind and constrain an explicit "no value moves" invariant, or (c) require `verifyWallet` to always enforce a signature (never allow `signerAddress == address(0)` to skip verification) and additionally re-derive actual balance deltas of every token the `stack.ops` calls touch, independent of the attacker-supplied `erc20TokenAddresses` array.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium for `HINKAL_EMPORIUM_ACTION_ID`, add Emporium as allowed recipient, seed Emporium with `TOKEN.balanceOf(Emporium) = 1000e18` (simulating in-flight funds).
2. As an unprivileged attacker EOA, construct `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `slippageValues = []`, `onChainCreation = []`, `inputNullifiers = []`, `outCommitments = []`, `encryptedOutputs = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress = address(Emporium)`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: address(TOKEN), invokeWallet:false, value:0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, 1000e18)})], ...}))`.
3. Generate a real proof for `MainEVMCircuitMin` with a self-chosen `messageSeed`, compute correct `calldataHash` via `CircomDataBuilder.getHashedCalldata`, and use `dimensions.tokenNumber = 0`.
4. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from attacker EOA.
5. Assert: `Hinkal.transact` does not revert; `TOKEN.balanceOf(address(Emporium))` drops from `1000e18` to `0`; `TOKEN.balanceOf(attacker)` increases by `1000e18`; and no `require` in `Hinkal.transact`'s balance/slippage checks (lines around `balanceDif == amountChanges + utxoAmount`) or `EmporiumUpgradeable.runAction`'s per-token loop fires, because both loops execute zero iterations over the empty `erc20TokenAddresses` array.

### Citations

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

**File:** contracts/CircomDataBuilder.sol (L134-148)
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
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
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
