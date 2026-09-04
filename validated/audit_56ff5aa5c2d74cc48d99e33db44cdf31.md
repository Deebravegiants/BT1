This confirms a legitimate, explicitly-supported "Emporium Min" flow: `formInputForCircom` in `contracts/CircomDataBuilder.sol` special-cases `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` and routes to `formInputEmporiumMin`, which is exactly the `MainEVMCircuitMin.circom` circuit (public inputs: `outTimeStamp`, `calldataHash` only — no `erc20TokenAddresses`, `amountChanges`, nullifiers, or commitments at all). [1](#0-0) [2](#0-1) 

### Title
Emporium "Min-circuit" path lets any caller drain pooled ETH left by other users' operations - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When `circomData.erc20TokenAddresses.length == 0` and `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, the protocol intentionally routes to the "Emporium Min" circuit/path (`formInputEmporiumMin`), which has no `amountChanges`/token accounting at all. In this path, `EmporiumUpgradeable.runAction`'s balance-difference safety check and `Hinkal.transact`'s `balanceDif`/`utxoAmount` equality check both iterate over `circomData.erc20TokenAddresses` and therefore execute zero times, so nothing constrains `EmporiumOperation.value` to the caller's own deposit.

### Finding Description
**Broken equality:** the intended invariant is "ETH spent by ops during this call ≤ ETH this caller deposited into Emporium during this same call" (enforced normally by the `balanceChange < 0` revert at `EmporiumUpgradeable.sol:142-144` and by the `balanceDif == amountChanges + utxoAmount` check at `Hinkal.sol:137-146`). Both checks are loops over `circomData.erc20TokenAddresses.length` [3](#0-2) [4](#0-3) .

Normally (tokenNumber ≥ 1, e.g., `erc20TokenAddresses=[address(0)]`), pre-funding of Emporium happens in `Hinkal._externalTransact` before `runAction` is invoked (transfer of `-deltaAmountChanges[i]` ETH into Emporium) [5](#0-4) , `balancesBefore` is snapshotted after that transfer, and any `op.value` spend exceeding the caller's own deposit `X` drives `balanceChange` negative once dust `D` is touched, reverting `BalanceChangeShouldBePositive()`. I verified this algebraically: spending `Y = X + Z` (Z of other users' dust) yields `balanceChange = -Z < 0` → revert. So in the normal path the described attack **is already blocked**.

However, `CircomDataBuilder.formInputForCircom` explicitly supports `circomData.erc20TokenAddresses.length == 0` for the Emporium action, in which case it uses `formInputEmporiumMin` (only `emporiumMessage`, `timeStamp`, `calldataHash` as public inputs) matching `MainEVMCircuitMin.circom`, which has no `amountChanges`, no nullifiers, no root/commitment constraints at all. `HinkalHelper.dimensionsCheck` only requires `erc20TokenAddresses.length == dimensions.tokenNumber` [6](#0-5)  — nothing forbids `tokenNumber == 0`.

With `erc20TokenAddresses = []`:
- `Hinkal._externalTransact`'s deposit loop doesn't run (0 iterations), so no ETH is pulled in from the attacker at all [7](#0-6) .
- `EmporiumUpgradeable.runAction`'s `balancesBefore`/`balancesAfter`/`balanceChange` accounting loop doesn't run (0 iterations) [8](#0-7) , so there is no check that ops don't exceed a deposit.
- `Hinkal.transact`'s post-call `balanceDif`/`utxoAmount` loop also doesn't run for the same reason [4](#0-3) .
- `verifyWallet` only checks EIP-712 signature/replay of `emporiumMessage`, not fund amounts [9](#0-8) .
- `op.value` inside `EmporiumOperation` is never a circuit-constrained signal in either the normal or Min circuit — it's only bound by the `calldataHash`/`getHashedCalldata` commitment to the caller's own crafted `externalActionMetadata` blob, not to any spend limit.

The attacker's exact call: craft `EmporiumStack{ops: [{endpoint: attackerAddr, value: <Emporium's full ETH balance>, callData: ""}]}`, set `circomData.erc20TokenAddresses = []`, `dimensions.tokenNumber = 0`, generate a valid proof for the `MainEVMCircuitMin` verifier (registered separately via `buildVerifierId(dimensions, HINKAL_EMPORIUM_ACTION_ID)`), sign the EIP-712 `EmporiumSignature` (if `stack.signerAddress != 0`) or leave `signerAddress = address(0)` to skip signature entirely, and call `Hinkal.transact`. `runAction` executes `op.endpoint.call{value: op.value}("")`, draining Emporium's entire ETH balance (built from prior unrelated users' dust) to the attacker, with zero balance accounting to stop it.

### Impact Explanation
Direct theft of pooled ETH belonging to other users who left residual balances in the shared `Emporium`/proxy contract from prior legitimate operations. This is Critical: theft of shielded/in-flight user funds via a pooled contract, with no per-depositor accounting to prevent it. The attack is repeatable every time dust accumulates in Emporium.

### Likelihood Explanation
Preconditions: (1) a verifier must be registered for `buildVerifierId(dimensions{tokenNumber:0,...}, HINKAL_EMPORIUM_ACTION_ID)` matching `MainEVMCircuitMin` — this is explicitly wired up in `CircomDataBuilder.formInputForCircom`, so the codebase clearly intends this path to exist and be usable; (2) Emporium must hold residual ETH from prior operations (dust), which is plausible since `EmporiumUpgradeable.handleOut` only returns change if `balanceChange > 0` is computed via the token-indexed loop, and any dust below what gets swept, or amounts intentionally left by design (e.g., relay fee residue, rounding), accumulates in the shared contract balance. Attacker cost is minimal: only proof generation for the trivial Min circuit and a valid EIP-712 signature setup (or `signerAddress = 0` to skip it). This is fully within the "unprivileged attacker" threat model.

Note: whether a `tokenNumber == 0` verifier is actually deployed in production is outside this repo's Solidity/circuit source (verifier contracts are out of scope), but the application-layer code (`CircomDataBuilder`, `dimensionsCheck`, `MainEVMCircuitMin.circom`) unambiguously supports and anticipates this zero-token Emporium path as a first-class feature, not a discouraged edge case.

### Recommendation
Do not skip balance accounting for the Emporium Min path. Either (a) require `EmporiumOperation.value` to sum to zero (or to be explicitly disallowed) whenever `erc20TokenAddresses.length == 0`, or (b) always run a native-ETH `balancesBefore`/`balancesAfter` check in `EmporiumUpgradeable.runAction` independent of `erc20TokenAddresses`, ensuring the contract's ETH balance never decreases (or only decreases by an amount tied to a real, circuit-verified deposit) as a result of `ops` execution, regardless of `tokenNumber`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (as `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]`), `HinkalWallet`, and register a verifier for `tokenNumber=0` matching `MainEVMCircuitMin` (or mock `VerifierFacade.verifyProof` to return true for this `verifierId`, consistent with the "locally generated proofs" requirement — using a real Groth16 setup for the trivial Min circuit is feasible since it only commits to `messageSeed`/`calldataHash`).
2. Simulate 3 independent prior sessions (different EOAs) each performing a correctly-dimensioned (`tokenNumber=1`, `erc20TokenAddresses=[address(0)]`) `transact()` that leaves 1 ETH of dust in Emporium (e.g., op.value less than what was deposited, verifying via the normal `balanceChange` path that dust legitimately accumulates). Assert `address(emporiumProxy).balance == 3 ether` after.
3. Attacker (a 4th, unrelated EOA with zero prior deposits) builds `CircomData` with `erc20TokenAddresses=[]`, `amountChanges=[]`, `dimensions.tokenNumber=0`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, and `externalActionMetadata` encoding `EmporiumStack{signerAddress:address(0), ops:[{endpoint:attackerEOA, invokeWallet:false, value:3 ether, callData:""}]}`.
4. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from attacker EOA with a valid proof for the Min verifier.
5. Assert: (a) call succeeds (no revert), (b) `attackerEOA.balance` increased by 3 ether, (c) `address(emporiumProxy).balance == 0`, (d) at no point was `attackerEOA`'s own contribution to Emporium (sum of ETH ever deposited by attacker via `amountChanges`) greater than 0 — i.e., "ETH spent by attacker's ops" (3 ETH) != "ETH attacker ever contributed" (0 ETH), proving the equality is broken and no per-depositor accounting exists to block it.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
```text
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

**File:** contracts/Hinkal.sol (L97-147)
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

**File:** contracts/HinkalHelper.sol (L64-71)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
```
