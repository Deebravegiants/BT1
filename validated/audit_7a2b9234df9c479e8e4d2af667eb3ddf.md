### Title
Emporium `Min`-circuit path lets an attacker execute arbitrary `ops` (including token/ETH transfers out of the shared Emporium contract) with zero balance-conservation checks - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When `circomData.erc20TokenAddresses` is empty, `CircomDataBuilder.formInputForCircom` routes the proof through `MainEVMCircuitMin`, which has no balance/UTXO constraints at all, and both `EmporiumUpgradeable.runAction` and `Hinkal.transact` iterate their balance-conservation checks strictly over `circomData.erc20TokenAddresses`. Since `stack.ops` (decoded from attacker-supplied `externalActionData.externalActionMetadata`) is completely independent of `erc20TokenAddresses`, an attacker can submit an empty token array while `stack.ops` still executes arbitrary `op.endpoint.call(op.callData)` calls, with `msg.sender` being the shared `EmporiumUpgradeable` contract itself.

### Finding Description
Equality claimed broken: `value moved by stack.ops (via op.endpoint.call) == 0` is asserted implicitly by the protocol's balance-conservation logic, but that logic never executes when `erc20TokenAddresses.length == 0`.

Trace:
- `formInputForCircom` selects `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` [1](#0-0) . `MainEVMCircuitMin` only constrains `outTimeStamp`, `calldataHash`, and derives `message` from `messageSeed` - there is no root hash, nullifier, amount, or UTXO constraint whatsoever [2](#0-1) .
- `EmporiumUpgradeable.runAction` decodes `stack` (containing `stack.ops`) directly from `circomData.externalActionData.externalActionMetadata` - this decoding is entirely independent of `circomData.erc20TokenAddresses` [3](#0-2) . For each op, if `stack.signerAddress == address(0)`, `verifyWallet` returns immediately without any signature check [4](#0-3) , and stateless ops are executed as `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == EmporiumUpgradeable` [5](#0-4) .
- The only balance-conservation logic in `runAction` loops `for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++)` - with an empty array this loop body (including the `BalanceChangeShouldBePositive` revert and `handleOut`) never runs [6](#0-5) .
- Symmetrically, `Hinkal.transact`'s balance-diff/slippage loop is bounded by `circomData.erc20TokenAddresses.length` [7](#0-6) , so it also does not execute for any token moved by the ops.
- `dimensionsCheck`/`checkOnchainCreation` only validate array-length consistency between `erc20TokenAddresses`, `amountChanges`, `onChainCreation`, `slippageValues`, `inputNullifiers`, `outCommitments` [8](#0-7)  - none of these constrain the content of `stack.ops`, and `getHashedCalldata` only binds `externalActionData` (thus `stack`) to the `calldataHash` the *attacker's own* proof commits to, which is self-consistent and provides no cross-check against `erc20TokenAddresses` or actual value moved.

Consequence: an attacker generating their own trivial `MainEVMCircuitMin` proof (no meaningful private-input knowledge required) can supply `erc20TokenAddresses=[]` and an `EmporiumStack` whose `ops` directly call e.g. `token.transfer(attacker, EmporiumBalance)` (no approval needed at all since `EmporiumUpgradeable` is itself the caller/holder) or trigger `transferFrom` against any stale approval, moving real value with **no** balance/slippage/UTXO check anywhere in the reachable path.

### Impact Explanation
`EmporiumUpgradeable` is a shared custody contract holding pooled ERC20/ETH balances backing many users' UTXOs. Because the Min-circuit path zeroes out every balance-conservation loop, an attacker can drain the contract's own token/ETH balance (via `token.transfer` calls Emporium itself makes) or exploit any stale ERC20 approval on the contract, with zero accounting anywhere in `runAction` or `Hinkal.transact`. This is direct theft of shielded/custodied user funds with no proof-of-ownership requirement - Critical severity, matching "direct theft of shielded or in-flight user funds" / "proof or nullifier verification bypass" (the Min circuit provides no such verification for this path).

### Likelihood Explanation
No privileged role is required. The attacker needs only: (1) a valid, already-existing `rootHashHinkal`/index pair (trivially available - any historical root works since Min circuit doesn't constrain it), (2) a self-generated `MainEVMCircuitMin` proof (Poseidon of an attacker-chosen `messageSeed`, no UTXO/nullifier knowledge needed), and (3) crafting `externalActionMetadata` with `stack.signerAddress = address(0)` and `stack.ops` calling `token.transfer(attacker, amount)` against a token the Emporium contract holds. This requires no victim cooperation, no stale approval, and no social engineering for the strongest form of the attack (draining Emporium's own held balance) - it is fully reachable purely through this repo's code paths and is repeatable for every ERC20/ETH the contract holds.

### Recommendation
Do not allow the zero-token "Min" circuit/path to be paired with a non-empty `stack.ops` that performs stateless calls capable of moving value. Either: (a) require `stack.ops.length == 0` (or restrict ops to non-value-moving calls) whenever `circomData.erc20TokenAddresses.length == 0`; (b) always compute balance snapshots for every token actually referenced by `stack.ops` endpoints (not just `circomData.erc20TokenAddresses`) and enforce conservation on them; or (c) require the Min circuit path only for actions with `externalActionId` other than Emporium, or add an explicit circuit/contract constraint binding `stack.ops` emptiness/no-value-transfer property to the Min path selection.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as allowed recipient), a mock ERC20 `T`, and fund `EmporiumUpgradeable` with `T` (simulating pooled custody from prior legitimate deposits).
2. Craft `CircomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `slippageValues = []`, `inputNullifiers = []`, `outCommitments = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({ops: [EmporiumOperation({endpoint: address(T), invokeWallet: false, value: 0, callData: abi.encodeCall(T.transfer, (attacker, T.balanceOf(address(emporium))))})], signerAddress: address(0), ...}))`.
3. Compute `calldataHash = CircomDataBuilder.getHashedCalldata(circomData)` and generate a valid `MainEVMCircuitMin` proof for a self-chosen `messageSeed` matching `emporiumMessage`/`message` linkage.
4. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from attacker EOA with an existing valid `rootHashHinkal`/index.
5. Assert: `T.balanceOf(attacker)` increases by the full amount, `T.balanceOf(address(emporium))` goes to zero, and no revert occurs in `runAction`'s `BalanceChangeShouldBePositive` check or `Hinkal.transact`'s slippage/balance-diff `require`s (because their loops never execute) - demonstrating `VALUE_CONSERVATION` is entirely bypassed for the drained token.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-160)
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

**File:** contracts/HinkalHelper.sol (L64-120)
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

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );

        uint previousNullifierAmount = circomData.inputNullifiers.length > 0
            ? circomData.inputNullifiers[0].length
            : 0;
        for (uint i = 1; i < circomData.inputNullifiers.length; i++) {
            require(
                circomData.inputNullifiers[i].length == previousNullifierAmount,
                "Nullifier amount should be equal"
            );
        }
        require(
            previousNullifierAmount == dimensions.nullifierAmount,
            "Actual and Claimed Nullifier Amount should be equal"
        );

        require(
            circomData.outCommitments.length == dimensions.tokenNumber,
            "OutCommitments number should be equal to token number"
        );

        uint previousCommitmentAmount = circomData.outCommitments.length > 0
            ? circomData.outCommitments[0].length
            : 0;

        for (uint i = 1; i < circomData.outCommitments.length; i++) {
            require(
                circomData.outCommitments[i].length == previousCommitmentAmount,
                "Commitment amount should be equal"
            );
        }
```
