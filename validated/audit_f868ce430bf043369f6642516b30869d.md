### Title
Emporium min-circuit path lets an attacker drain Emporium's ERC20 balances uncounted - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When `circomData.erc20TokenAddresses` is empty, `CircomDataBuilder.formInputForCircom` routes Emporium actions to the `MainEVMCircuitMin` public-input set, which only constrains `emporiumMessage`, `timeStamp`, and `calldataHash` and never binds `erc20TokenAddresses`/`amountChanges` into the circuit at all. `EmporiumUpgradeable.runAction` still executes attacker-controlled `op.endpoint.call(op.callData)` for every op in `stack.ops` (with `stack.signerAddress == address(0)`, `verifyWallet` is a no-op with no signature check), so an attacker can make Emporium call `IERC20.transfer` on any token T it holds, moving out all of T's balance while every balance-accounting loop iterates 0 times because the array is empty.

### Finding Description
The broken equality is: **tokens leaving an action == -deltaAmountChanges it received**, i.e. for token T, `balancesBefore[T] - balancesAfter[T]` must equal something reconciled against `deltaAmountChanges[T]`/`amountChanges[T]`. With `circomData.erc20TokenAddresses = []`:

- In `EmporiumUpgradeable.runAction`, `balancesBefore`/`balancesAfter` are computed via `getBalancesForArray(circomData.erc20TokenAddresses)` [1](#0-0) , and the reconciliation loop that checks `balanceChange` and calls `handleOut` only iterates over `circomData.erc20TokenAddresses.length` [2](#0-1) . With an empty array, this loop never runs, so any balance change to token T is never checked or refunded to the user.
- The ops loop executes `op.endpoint.call{value: op.value}(op.callData)` unconditionally for stateless interactions when the selector isn't `callHinkalWallet`/`doSendToRelay` [3](#0-2) . There is no check that `op.endpoint` is a token in `erc20TokenAddresses`, nor any allow-list on `op.endpoint`.
- `verifyWallet` only enforces a signature when `stack.signerAddress != address(0)`; with `signerAddress == address(0)` it just marks the message used and returns [4](#0-3) , so the attacker fully controls `stack.ops` (endpoint, callData, value) with no wallet-owner signature required.
- Back in `Hinkal.transact`, `oldBalances`/`newBalances` are likewise computed with `circomData.erc20TokenAddresses` (empty), and the entire balance-diff/slippage/utxo-reconciliation loop is skipped because `circomData.erc20TokenAddresses.length == 0` [5](#0-4) .
- `CircomDataBuilder.formInputForCircom` explicitly special-cases this: if `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`, it calls `formInputEmporiumMin`, which forms public inputs from only `emporiumMessage`, `timeStamp`, `calldataHash` [6](#0-5) , matching `MainEVMCircuitMin.circom`'s public signals (`outTimeStamp`, `calldataHash`) [7](#0-6) . No erc20 token, amount, nullifier, or UTXO fields are proof-constrained on this path.
- `getHashedCalldata`/`calldataHash` does bind `externalActionData` (hence `stack.ops`) into `calldataHash`, and `performHinkalChecks` verifies `getHashedCalldata(circomData) == circomData.calldataHash` [8](#0-7) . This only proves internal consistency of the calldata the attacker supplied — it does not constrain `op.endpoint`/`op.callData` to be benign, and does not require `erc20TokenAddresses` to include every token actually touched by the ops.
- `onlyAllowedRecipient` on `runAction` only checks that `msg.sender` (the Hinkal contract) is an allowed recipient — it does not restrict `op.endpoint` inside the metadata [9](#0-8) .

Attacker's call: `Hinkal.transact(a,b,c,dimensions,circomData)` with a valid `MainEVMCircuitMin` proof, `circomData.erc20TokenAddresses = []`, `circomData.externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata` decoding to `EmporiumStack{signerAddress: address(0), ops: [{endpoint: T, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, T.balanceOf(emporium))}]}`. Every check that exists (`performHinkalChecks`, `verifyProof`, `rootHashExists`, `dimensionsCheck`, `checkOnchainCreation`, Hinkal's balance/slippage loop, Emporium's own balance loop, `verifyWallet`) either doesn't apply to token T (not in the empty array) or is a no-op for `signerAddress == address(0)`.

### Impact Explanation
Direct theft of any ERC20 balance currently held by the Emporium contract (residue from other users' deposits, swaps, or in-flight operations), with no accounting or refund, and no signature requirement since `signerAddress == address(0)` bypasses `verifyWallet`. This matches "Critical - direct theft of shielded or in-flight user funds ... proof or nullifier verification bypass," since the min-circuit's public inputs never constrain the executed calls or the tokens moved. The attack is repeatable for every token Emporium holds and every time it accumulates a positive balance, at the cost of only one proof generation (trivial with `MainEVMCircuitMin`, which has no meaningful private witness beyond `messageSeed`).

### Likelihood Explanation
Preconditions: Emporium must hold a nonzero balance of token T (achievable from normal deposit/swap flows where funds transiently sit in Emporium, or the attacker can seed it themselves via their own prior Emporium action, e.g., deposit T into Emporium via a normal action and immediately drain via this min-circuit call). Attacker needs only: (1) ability to generate a Groth16 proof for the already-deployed `MainEVMCircuitMin` circuit — cheap, no private data about other users required; (2) ability to craft `CircomData`/`EmporiumStack` fields, which is explicitly permitted to an unprivileged actor. No privileged role, relay, or other user's key is required. Feasibility is high and fully within the described attacker capability model.

### Recommendation
In `EmporiumUpgradeable.runAction`, do not rely solely on `circomData.erc20TokenAddresses` to determine which balances to reconcile — either (a) forbid the min-circuit/empty-array path from reaching `_externalTransact`/`runAction` entirely (route `erc20TokenAddresses.length == 0` only to a no-call, pure-message-verification action), or (b) require that every `op.endpoint` invoked as a stateless call be present in `circomData.erc20TokenAddresses` (or another allow-listed set) and that the resulting balance deltas for all tokens actually touched — not just the ones declared in `erc20TokenAddresses` — are computed and reconciled, e.g. by snapshotting/comparing balances of `op.endpoint` when it is itself an ERC20 token, or by requiring `erc20TokenAddresses.length > 0` whenever `stack.ops.length > 0`.

### Proof of Concept
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (registered under `HINKAL_EMPORIUM_ACTION_ID`, `Hinkal` set as allowed recipient), and the `MainEVMCircuitMin` verifier.
2. Deploy a mock ERC20 `T`, mint `1000e18` to `Emporium` (simulating leftover balance from another user's flow).
3. Off-chain: generate a Groth16 proof for `MainEVMCircuitMin` with arbitrary `messageSeed`, public inputs `outTimeStamp`, `calldataHash` matching a crafted `CircomData` with:
   - `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `slippageValues = []`, `inputNullifiers = []`, `outCommitments = []`
   - `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress = <Emporium address>`
   - `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{v:0,r:0,s:0, signerAddress: address(0), ops: [EmporiumOperation{endpoint: T, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, 1000e18)}], maxFee: 0, deadline: type(uint256).max})`
4. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from attacker EOA.
5. Assert: `T.balanceOf(attacker)` increased by `1000e18`, `T.balanceOf(emporium)` decreased by `1000e18`, while `circomData.erc20TokenAddresses`/`amountChanges` are length 0 (i.e., the on-chain accounting recorded zero token movement for T despite the nonzero real transfer) — confirming `0 == nonzero` was never checked.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
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

**File:** contracts/Hinkal.sol (L78-147)
```text
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
