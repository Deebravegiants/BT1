### Title
Zero-token Emporium Min-circuit path lets attacker drain Emporium's arbitrary ERC20/ETH holdings via unaccounted `op.endpoint.call` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol / contracts/CircomDataBuilder.sol)

### Summary
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only constrains `emporiumMessage`, `timeStamp`, and `calldataHash` (i.e., `message == Poseidon(messageSeed)`), doing no accounting on funds moved. An attacker can supply an `EmporiumStack` with `signerAddress == address(0)` (skipping the EIP-712 signature check in `verifyWallet`) whose `ops` array performs arbitrary `op.endpoint.call{value: op.value}(op.callData)` calls, including calling any ERC20 token's `transfer` function to move tokens Emporium holds to the attacker, all while every balance-accounting loop in `Hinkal.transact` and `EmporiumUpgradeable.runAction` iterates the empty `erc20TokenAddresses` array and enforces nothing.

### Finding Description
The invariant the protocol needs is: **assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter` (and in `Hinkal.transact`'s `oldBalances`/`newBalances`/slippage/balance-diff checks)**. This equality is broken.

Path:
1. Attacker calls `Hinkal.transact` with `dimensions.tokenNumber = 0` and `circomData.erc20TokenAddresses.length == 0`, `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalAddress` = the registered Emporium address.
2. `HinkalHelper.performHinkalChecks` calls `dimensionsCheck`, which only requires `erc20TokenAddresses.length == dimensions.tokenNumber` — both attacker-controlled and consistently zero, so it passes: [1](#0-0) .
3. `CircomDataBuilder.formInputForCircom` detects the Emporium+zero-token condition and calls `formInputEmporiumMin`, producing a public input vector that only proves `message == Poseidon(messageSeed)`, `timeStamp`, `calldataHash` — no root, no nullifiers, no amountChanges are constrained by the circuit at all: [2](#0-1)  and [3](#0-2) .
4. `Hinkal.transact` calls `_externalTransact`, which builds `deltaAmountChanges` over the empty `erc20TokenAddresses` array (empty) and calls `EmporiumUpgradeable.runAction`: [4](#0-3) .
5. In `runAction`, `balancesBefore`/`balancesAfter` are computed over the empty token array (no-ops), and `verifyWallet` returns immediately without any signature check because `stack.signerAddress == address(0)`: [5](#0-4) .
6. The `ops` loop then executes `op.endpoint.call{value: op.value}(op.callData)` for every op in the attacker-supplied `EmporiumStack`, with only a selector-blacklist for `callHinkalWallet`/`doSendToRelay` — any other call (e.g., `USDC.transfer(attacker, balanceOf(Emporium))`) is executed with `msg.sender == Emporium`: [6](#0-5) .
7. The post-loop reconciliation in `runAction` only iterates `circomData.erc20TokenAddresses` (empty), so the stolen token's balance change is never inspected or reverted: [7](#0-6) .
8. Back in `Hinkal.transact`, `oldBalances`/`newBalances` and the slippage/balance-diff `require`s also iterate the same empty `circomData.erc20TokenAddresses`, so nothing catches the theft there either: [8](#0-7) .

No guard (`performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `verifyProof`, `rootHashExists`, `insertNullifiers`, `onlyAllowedRecipient`) restricts what `op.endpoint`/`op.callData` can be, nor ties them to `erc20TokenAddresses`. `onlyAllowedRecipient` only checks that `msg.sender == hinkalAddress` (i.e., only Hinkal can call `runAction`), it does not restrict `ops` content.

### Impact Explanation
Any unprivileged attacker can drain any ERC20 token or native ETH balance held by the Emporium contract (from other users' deposits, in-flight Emporium operations, or relay fee floats) directly to their own address, with zero circuit-level or accounting-level constraint on the amount moved. This is direct theft of protocol/in-flight/shielded funds, fully repeatable as long as Emporium holds a nonzero balance of any token, matching Critical severity ("direct theft of shielded or in-flight user funds").

### Likelihood Explanation
Preconditions: Emporium (or any external action reachable this way) must hold a nonzero token/ETH balance at call time — routine because users route deposits/operations through it. The attacker needs no special role: any EOA can build `CircomData`/`Dimensions` with `erc20TokenAddresses.length == 0`, craft an `EmporiumStack` with `signerAddress == address(0)` and an arbitrary `ops` array, and generate a trivial Min-circuit proof (only requires knowing a `messageSeed` they themselves choose). Cost is a single transaction; the attack is fully repeatable each time Emporium accrues balance.

### Recommendation
- Reject the Emporium Min-circuit path (or any Emporium `runAction` invocation) whenever `stack.ops` targets addresses/selectors not present in `circomData.erc20TokenAddresses`, or better, require `erc20TokenAddresses` to enumerate every token/ETH touched by `ops` and always run full balance accounting regardless of array length.
- Do not allow `formInputEmporiumMin` (near-empty proof) to be paired with unconstrained arbitrary `ops`; the Min circuit should only be usable for a strictly limited, provably-safe subset of actions (e.g., only wallet-authenticated stateful interactions), or require `signerAddress != address(0)` whenever the Min path is used so `verifyWallet`'s signature check cannot be bypassed.
- Alternatively, compute `balancesBefore`/`balancesAfter` over the full set of addresses/tokens actually touched by `stack.ops` (derived from calldata inspection or an explicit attacker-independent allowlist), not solely `circomData.erc20TokenAddresses`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium as external action with `HINKAL_EMPORIUM_ACTION_ID`.
2. Fund Emporium with e.g. 1000 USDC (simulate prior deposits/relay float).
3. Attacker builds `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `slippageValues = []`, `inputNullifiers = []`, `outCommitments = []`, `externalActionData = {externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalAddress: emporiumAddr, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: usdc, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e6))}], maxFee: 0, deadline: type(uint256).max})}`, `dimensions.tokenNumber = 0`.
4. Generate a locally-computed Min-circuit proof for `message = Poseidon(messageSeed)` matching `emporiumMessage`, with matching `calldataHash = getHashedCalldata(circomData)`.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from attacker EOA.
6. Assert: `USDC.balanceOf(attacker)` increases by 1000e6 and `USDC.balanceOf(emporiumAddr)` decreases by 1000e6; assert the transaction does not revert; assert `balanceDif == amountChanges[i] + utxoAmount` check in `Hinkal.transact` is never evaluated for USDC (loop bound is 0), proving the equality "assets moved == assets accounted" is violated.

### Citations

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
