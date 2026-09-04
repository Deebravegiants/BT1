### Title
Emporium Min-proof path lets an unprivileged attacker run arbitrary, unaccounted external calls from Emporium's identity - (File: contracts/CircomDataBuilder.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes the proof to `formInputEmporiumMin`, whose corresponding circuit (`MainEVMCircuitMin.circom`) proves only `message == Poseidon(messageSeed)` and does not constrain `rootHashHinkal`, nullifiers, `amountChanges`, or the `EmporiumStack`. `EmporiumUpgradeable.runAction` then executes `stack.ops` (arbitrary `endpoint.call{value: op.value}(op.callData)`) whenever `stack.signerAddress == address(0)`, with balance accounting driven entirely by `circomData.erc20TokenAddresses`, which is empty by construction of this path. The equality "assets Emporium can move in a tx == assets accounted in balancesBefore/balancesAfter" is broken: Emporium can move value (ETH/tokens it holds, or calls into other `onlyAllowedRecipient` actions that trust Emporium's `msg.sender`) while the accounting arrays are empty and check nothing.

### Finding Description
The broken equality: `sum(effects of stack.ops executed by Emporium) == sum(balancesAfter[i]-balancesBefore[i] for i in circomData.erc20TokenAddresses)`. When `erc20TokenAddresses.length == 0`, the right side is trivially `0` regardless of the left side.

Path:
1. `formInputForCircom` (contracts/CircomDataBuilder.sol:134-148) selects `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` — both fields are attacker-controlled in `CircomData`. [1](#0-0) 
2. `formInputEmporiumMin` produces only 3 public signals: `emporiumMessage`, `timeStamp`, `calldataHash` (contracts/CircomDataBuilder.sol:150-161). [2](#0-1) 
3. The matching circuit, `MainEVMCircuitMin.circom`, only computes `message <== Poseidon(1)([messageSeed])` and never constrains `outTimeStamp` or `calldataHash` inside the circuit body — an attacker who freely picks `messageSeed` can trivially produce any `emporiumMessage` and a valid proof, with no ownership of a real UTXO/leaf, no nullifier spend, and no tie to `rootHashHinkal`. [3](#0-2) 
4. `performHinkalChecks` in `HinkalHelper.sol` only re-derives `calldataHash` from the attacker's own submitted `circomData` (self-consistency, not authorization) and calls `dimensionsCheck`/`checkOnchainCreation`, none of which force `erc20TokenAddresses.length > 0` or require real ownership for the Emporium-Min branch. [4](#0-3) 
5. `Hinkal.transact` still calls `rootHashExists` (any historical, public root is acceptable) then, because `circomData.externalActionData.externalActionId != 0`, calls `_externalTransact`, which dispatches into `EmporiumUpgradeable.runAction`. [5](#0-4) 
6. `EmporiumUpgradeable.runAction` decodes attacker-supplied `EmporiumStack` from `externalActionData.externalActionMetadata`, computes `balancesBefore/After` over the (empty) `circomData.erc20TokenAddresses`, calls `verifyWallet` (which, for `stack.signerAddress == address(0)`, just marks the message used and returns — no signature required), then iterates `stack.ops`. Since `stack.signerAddress == address(0)`, every op falls into the "Stateless Interaction" branch and executes `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == Emporium` for arbitrary attacker-chosen `endpoint`/`callData`/`value` (only `callHinkalWallet`/`doSendToRelay` selectors are blocked). [6](#0-5) 
7. Because `circomData.erc20TokenAddresses.length == 0`, the post-loop accounting in `runAction` (lines 122-159) and the outer accounting in `Hinkal.transact` (`oldBalances`/`newBalances`/slippage loop, lines 78-146) all iterate zero times — nothing about the effects of `stack.ops` is checked, reverted, or captured into `utxoSet`. [7](#0-6) 

Exploit flow: attacker calls `Hinkal.transact` with `originalSender == msg.sender`, `relay == address(0)`, `erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata` = an `EmporiumStack{ signerAddress: address(0), ops: [ { endpoint: <target>, invokeWallet: false, value: 0, callData: <arbitrary, e.g. IERC20.transfer(attacker, EmporiumBalance) or a call into another allowlisted action that trusts Emporium as msg.sender> } ] }`, `emporiumMessage = Poseidon(chosenSeed)`, and a trivially-generated Min proof. `runAction` executes the op(s) as Emporium, moving any funds Emporium holds (including fee-on-transfer tokens where the "stated" and "delivered" amounts diverge — since nothing here compares the two, the discrepancy is irrelevant, further proving no accounting exists at all) or invoking another `onlyAllowedRecipient`-gated action that trusts `msg.sender == Emporium`, with zero checks anywhere in the call. Existing guards (`performHinkalChecks`, `rootHashExists`, `insertNullifiers`, `verifyWallet` signature check) are all either bypassed (signature check skipped when `signerAddress==0`) or vacuous for this branch (they check self-consistency of attacker-chosen data, not real ownership or accounting).

### Impact Explanation
Any unprivileged party can direct the Emporium contract to execute arbitrary external calls from Emporium's own address, with no balance/slippage check whatsoever, using an almost-free self-generated proof that requires no real deposit, no UTXO ownership, and no relayer signature. Anything Emporium holds (ETH sent via `op.value`, ERC20 balances left from other operations, in-flight funds) can be drained by the attacker, and any other external action that whitelists Emporium as an `onlyAllowedRecipient` caller can be invoked with a completely attacker-forged inner `CircomData`/`deltaAmountChanges`, since that inner call is not tied to any proof at all. This is direct theft of protocol/in-flight/user funds routed through or held by Emporium — Critical severity, and repeatable per transaction (bounded only by how much value Emporium happens to hold at call time).

### Likelihood Explanation
Preconditions: Emporium must hold or be able to acquire some transferable value during the transaction (ETH/tokens sitting in the contract, or reachable via a chained call into a trusting action), and a historical Merkle root must exist (any prior root works, publicly known). No privileged role, no victim collusion, no relayer is required. The attacker cost is only gas plus generating a trivial Groth16 proof for `MainEVMCircuitMin` (Poseidon preimage of a self-chosen seed) — computationally negligible and fully within an unprivileged EOA's capability. This is highly feasible and repeatable.

### Recommendation
Do not allow the Emporium Min path to skip balance/ownership accounting when `stack.ops` can invoke arbitrary external calls. Specifically: (1) forbid stateless `op.endpoint.call` execution unless `circomData.erc20TokenAddresses` (and the corresponding balance-diff accounting) actually cover every token/asset that any op in `stack.ops` could move, or (2) require a valid `stack.signerAddress` signature (disallow `address(0)` bypass) whenever `stack.ops` targets non-zero `value` or calls into other registered external actions, or (3) constrain the Min circuit to also bind real ownership (root/nullifier) rather than only `message == Poseidon(messageSeed)`, and enforce `erc20TokenAddresses.length == 0` only when `stack.ops` is proven to have no economically-relevant external effect (e.g., restrict Min-path ops to a safelist that cannot move value or call other `onlyAllowedRecipient` actions).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (add Emporium to `allowedRecipients`), and register `HINKAL_EMPORIUM_ACTION_ID -> EmporiumUpgradeable` in `Hinkal.registerExternalAction`.
2. Fund `EmporiumUpgradeable` with, e.g., 10 ETH and 1000 units of a mock ERC20 (or a fee-on-transfer ERC20) to simulate in-flight/dust balances.
3. Generate a valid Groth16 proof for `MainEVMCircuitMin` locally with an attacker-chosen `messageSeed`, computing `emporiumMessage = Poseidon(messageSeed)`.
4. Craft `CircomData` with `erc20TokenAddresses = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: address(mockToken or attackerContract), invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, 1000)}], maxFee:0, deadline:0, v:0, r:0, s:0})`, matching `calldataHash`, valid `rootHashHinkal`/`rootHashHinkalIndex` from a prior state, empty `inputNullifiers`/`outCommitments`/`amountChanges`/`slippageValues`.
5. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from an attacker EOA with no prior deposits.
6. Assert: transaction succeeds, `mockToken.balanceOf(attacker)` increases by 1000, `EmporiumUpgradeable`'s token balance decreases by 1000 (or by more than 1000 delivered for a fee-on-transfer token, showing no delivered-vs-stated accounting), and no `require` in `Hinkal.transact`'s balance/slippage loop (lines 97-146) or `EmporiumUpgradeable.runAction`'s balance loop (lines 122-159) ever executed (both loops bound by `circomData.erc20TokenAddresses.length == 0`). [8](#0-7)

### Citations

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

**File:** contracts/Hinkal.sol (L30-146)
```text
    function transact(
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        Dimensions calldata dimensions,
        CircomData calldata circomData
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
        hinkalHelper.performSideEffects(circomData);

        {
            if (circomData.hookData.preHookContract != address(0)) {
                IPreTransactHook transactHook = IPreTransactHook(
                    circomData.hookData.preHookContract
                );
                transactHook.preTransact(circomData);
            }

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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-118)
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
