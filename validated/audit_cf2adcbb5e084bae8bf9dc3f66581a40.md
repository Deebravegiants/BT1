### Title
Zero-token Emporium-min proof path lets any EOA drain EmporiumUpgradeable's ETH/ERC20 balance with no balance-conservation check anywhere - (File: contracts/Hinkal.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol, contracts/CircomDataBuilder.sol, circuits/MainEVMCircuitMin.circom)

### Summary
`CircomDataBuilder.formInputForCircom` deliberately routes any `transact()` call with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0` to `formInputEmporiumMin`, which is verified against `MainEVMCircuitMin.circom` — a circuit that only checks `message = Poseidon(messageSeed)` against `emporiumMessage`/`calldataHash`/`timeStamp`, with **no** nullifier, root, or UTXO-ownership constraint. Because both the Hinkal-level balance loop (`Hinkal.sol:97-147`) and the Emporium-level balance loop (`EmporiumUpgradeable.runAction:132-151`) iterate over the *same* now-empty `erc20TokenAddresses` array, they run zero times, while `EmporiumStack.ops` (an attacker-controlled, independently-sized array) still executes real `op.endpoint.call{value: op.value}(op.callData)` calls in stateless mode (`stack.signerAddress == address(0)`), letting an unprivileged EOA drain EmporiumUpgradeable's real ETH/ERC20 balance with zero on-chain accounting.

### Finding Description
The equality that is supposed to hold and never gets evaluated:
`balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount` for every token touched — see `Hinkal.sol:137-146`. The equivalent internal check in Emporium, `balanceChange >= 0` (`EmporiumUpgradeable.sol:142-144`, `BalanceChangeShouldBePositive`), is also gated on the same array.

Path:
1. `CircomDataBuilder.formInputForCircom` (`contracts/CircomDataBuilder.sol:139-148`) special-cases `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` → `formInputEmporiumMin` (`:150-161`), whose only public inputs are `emporiumMessage`, `timeStamp`, `calldataHash`.
2. This corresponds to `MainEVMCircuitMin.circom` (`circuits/MainEVMCircuitMin.circom:1-18`), which only constrains `message <== Poseidon(1)([messageSeed])` — no nullifier/root/UTXO logic at all. An attacker can trivially generate a valid proof for **any** `messageSeed`/`emporiumMessage` without owning any shielded funds.
3. `dimensionsCheck` (`HinkalHelper.sol:64-171`) is satisfied by simply setting `dimensions = {tokenNumber:0, nullifierAmount:0, outputAmount:0}` and all corresponding arrays (`erc20TokenAddresses`, `amountChanges`, `onChainCreation`, `slippageValues`, `inputNullifiers`, `outCommitments`, `encryptedOutputs`) to empty. `rootHashExists` still passes trivially with any historical root.
4. `Hinkal.transact()` (`Hinkal.sol:97-147`) computes `oldBalances`/`newBalances` via `getBalancesForArray(circomData.erc20TokenAddresses)` — empty array, loop runs 0 times. [1](#0-0) 
5. Since `externalActionId != 0`, `_externalTransact` calls `EmporiumUpgradeable.runAction(circomData, deltaAmountChanges=[])`. [2](#0-1) 
6. Inside `runAction`, `stack = abi.decode(circomData.externalActionData.externalActionMetadata, (EmporiumStack))` is fully attacker-controlled. `verifyWallet` with `stack.signerAddress == address(0)` performs **no signature check**, only marks the message used. [3](#0-2) 
7. The `stack.ops` loop (`:91-118`) is sized by `stack.ops.length`, independent of `erc20TokenAddresses.length`. In stateless mode it executes `op.endpoint.call{value: op.value}(op.callData)` to any attacker-chosen `endpoint` (e.g., a real ERC20 token contract, calling `transfer(attacker, balance)` as `msg.sender = EmporiumUpgradeable`, or any address to siphon ETH via `op.value`). [4](#0-3) 
8. `payRelayFees` is bypassed by setting `feeStructure.flatFee = 0`.
9. `balancesAfter`/`balancesBefore` comparison loop (`:132-151`) also iterates over the empty `erc20TokenAddresses`, so `BalanceChangeShouldBePositive` never fires despite the drain.
10. Back in `Hinkal.sol`, `utxoSet.length == 0`; `insertNullifiers`/`insertCommitments` operate on empty arrays — the attacker's transaction leaves no trace in the shielded state tree.

No existing guard (`performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `verifyProof`, `rootHashExists`, `onlyAllowedRecipient`, `nonReentrant`) constrains `stack.ops` to the declared token set, and the circuit selected for this exact combination (`erc20TokenAddresses.length == 0`, Emporium action) enforces nothing about balances by design.

### Impact Explanation
Any unprivileged EOA can drain EmporiumUpgradeable's own ETH balance and any ERC20 tokens it holds (accumulated relay fees, leftover balances, or funds routed through it) to an address of their choosing, with no signature, no nullifier consumption, and no balance-conservation check anywhere in the call path. This is theft of protocol/relay funds held in the Emporium contract — Critical/High per the stated severity matrix (theft of protocol/relay fees, or worse if Emporium ever custodies user funds mid-flow). The attack is repeatable per unused `emporiumMessage` nonce and bounded only by Emporium's balance.

### Likelihood Explanation
Precondition: the owner must have registered a verifier for `verifierId = keccak256(tokenNumber=0, nullifierAmount=0, outputAmount=0, HINKAL_EMPORIUM_ACTION_ID)`. This is not a hypothetical edge case — `CircomDataBuilder.formInputEmporiumMin` and `MainEVMCircuitMin.circom` exist specifically to serve this exact dimension combination, indicating it is an intended, supported production code path (presumably meant only for signer-authenticated stateful ops). No other privileged precondition, victim key, or special timing is required; attacker cost is one proof generation (trivial, since the circuit has no UTXO constraints) plus gas.

### Recommendation
Decouple Emporium's op execution from `erc20TokenAddresses`: enforce that stateless-mode (`signerAddress == address(0)`) ops can only interact with tokens/amounts explicitly declared and balance-checked in `circomData.erc20TokenAddresses`/`amountChanges`, or disallow the `erc20TokenAddresses.length == 0` / min-circuit path entirely for external actions that can trigger `op.endpoint.call`. At minimum, require `stack.ops.length == 0` whenever `erc20TokenAddresses.length == 0`, and ensure the min-circuit verifier registered for Emporium enforces `stack.signerAddress != address(0)` (i.e., disallow stateless ops under the min-dimension verifier).

### Proof of Concept
Hardhat fork/unit test:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (proxy), register a verifier stub for `verifierId = buildVerifierId({tokenNumber:0,nullifierAmount:0,outputAmount:0}, HINKAL_EMPORIUM_ACTION_ID)` that accepts any valid Poseidon-preimage proof (locally generate a real Groth16 proof from `MainEVMCircuitMin.circom` with an arbitrary `messageSeed`).
2. Fund `EmporiumUpgradeable` with 10 ETH and 1000 units of a mock ERC20 (simulating accrued fees/deposits).
3. Attacker EOA (no prior deposits, no UTXOs) builds `CircomData` with: `erc20TokenAddresses=[]`, `amountChanges=[]`, `onChainCreation=[]`, `slippageValues=[]`, `inputNullifiers=[]`, `outCommitments=[]`, `feeStructure.flatFee=0`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress = EmporiumUpgradeable`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: mockERC20, invokeWallet:false, value:0, callData: transfer(attacker, 1000)}, {endpoint: attacker, invokeWallet:false, value: 10 ether, callData: ""}]})`.
4. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from attacker EOA.
5. Assert: transaction does **not** revert; `EmporiumUpgradeable` ETH balance goes from 10 → 0 and ERC20 balance from 1000 → 0; attacker balances increase accordingly.
6. Assert both sides of the broken equality: `newBalances.length == 0 == oldBalances.length` (Hinkal.sol loop never runs) and `balancesAfter.length == 0 == balancesBefore.length` (Emporium loop never runs), confirming `balanceDif >= slippageValues[i]` and `balanceDif == amountChanges[i] + utxoAmount` are never evaluated despite real value leaving the contract. [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-160)
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
        }

        return utxoSet;
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
