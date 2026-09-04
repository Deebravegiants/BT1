### Title
Emporium Min-circuit path lets an unprivileged attacker execute arbitrary calls from Emporium's identity with zero balance accounting - (File: contracts/CircomDataBuilder.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, whose circuit (`MainEVMCircuitMin`) only proves `message == Poseidon(messageSeed)` and does not bind `rootHashHinkal`, nullifiers, `amountChanges`, or `externalActionData` at all. `EmporiumUpgradeable.runAction` decodes an attacker-controlled `EmporiumStack` and, if `signerAddress == address(0)`, skips the EIP-712 signature check entirely in `verifyWallet`, then executes arbitrary `op.endpoint.call{value: op.value}(op.callData)` from Emporium's own address. Since `erc20TokenAddresses` is empty, the before/after balance-accounting loop iterates zero times, so any assets moved by the call are entirely unaccounted for.

### Finding Description
The invariant that should hold is: **every asset Emporium's identity can move during `runAction` must be reflected in `balancesBefore`/`balancesAfter` for `circomData.erc20TokenAddresses`.** In the Min path this is broken because the token array driving that accounting loop is empty by construction (`erc20TokenAddresses.length == 0` is exactly the condition that selects the Min circuit in `formInputForCircom`), while `stack.ops` (decoded from `externalActionData.externalActionMetadata`) is unconstrained by the proof or by dimension checks and can contain any number of arbitrary calls.

Path: `Hinkal.transact` → `hinkalHelper.performHinkalChecks` → `CircomDataBuilder.formInputForCircom` selects `formInputEmporiumMin` (only `emporiumMessage`, `timeStamp`, `calldataHash` as inputs) [1](#0-0)  → `verifyProof` against `MainEVMCircuitMin`, which only checks `message === Poseidon(messageSeed)` and says nothing about `rootHashHinkal`, ownership, or any external action fields [2](#0-1)  → `rootHashExists` is checked against `circomData.rootHashHinkal`/`rootHashHinkalIndex`, but since the Min circuit never consumes `rootHashHinkal` as a signal, the attacker can supply any historically-valid root without proving any relationship to it [3](#0-2)  → `_externalTransact` looks up `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]` and calls `EmporiumUpgradeable.runAction` [4](#0-3)  → `EmporiumUpgradeable.runAction` decodes `EmporiumStack`, computes `balancesBefore` over the (empty) `erc20TokenAddresses` array, calls `verifyWallet`, then iterates `stack.ops` [5](#0-4) . In `verifyWallet`, if `stack.signerAddress == address(0)`, the function returns immediately after marking `usedMessages[emporiumMessage] = true`, without any signature check [6](#0-5) . With `signerAddress == 0`, each op takes the "Case 2: Stateless Interaction" branch and performs `op.endpoint.call{value: op.value}(op.callData)` directly, msg.sender being the Emporium contract itself [7](#0-6) . Finally, `balancesAfter`/`balancesBefore` are diffed only over `circomData.erc20TokenAddresses`, which is empty, so the loop that would otherwise revert on unaccounted balance changes (`BalanceChangeShouldBePositive`) never executes for any token touched by the raw calls [8](#0-7) .

**Root cause**: the check `erc20TokenAddresses.length == 0` that selects the Min proof path is orthogonal to and unconstrained against the contents of `stack.ops`, which come from `externalActionMetadata`. There is no requirement that a Min-path transaction perform zero external calls, and `verifyWallet`'s only gate against unauthorized raw calls is a signature check that is explicitly skipped when `signerAddress == address(0)`.

The only constraint the attacker must satisfy to reach this state is `getHashedCalldata(circomData) == circomData.calldataHash`, which is a self-consistency hash the attacker computes themselves off-chain (not an ownership or authorization check) [9](#0-8) . `dimensionsCheck` with `dimensions.tokenNumber == 0` is satisfied trivially by empty arrays [10](#0-9) , and `checkOnchainCreation`'s loop is a no-op over an empty array [11](#0-10) .

**Caveat on impact**: for the attacker's raw call to actually move a victim's funds, it depends on some ERC20 token or contract having granted a standing approval or privilege *to the Emporium contract address specifically* (e.g., `token.transferFrom(victim, attacker, amount)` consuming an allowance where `spender == Emporium`), or Emporium itself holding balances left over from a prior interaction (the code comment at line 141 acknowledges "there were some funds on emporium before the call" as an expected state). I could not find, within the available index, code that would cause arbitrary third-party users to grant ERC20 approvals directly to the Emporium contract as part of a normal Hinkal flow (approvals in the swap/LI.FI flows typically originate from Hinkal or from Emporium's own balance, not from external wallets approving Emporium). Whether such a standing-approval precondition is realistic in production usage is not verifiable from the code alone.

### Impact Explanation
If a standing approval or leftover balance exists that Emporium's address can draw on (from prior legitimate `runAction` calls, e.g., partially-filled swaps, refunds, or contracts that pre-approve Emporium as a spender), an attacker can call `Hinkal.transact` with a trivial Min-circuit proof and a crafted `EmporiumStack` (`signerAddress == 0`, arbitrary `ops`) to move that value to themselves with zero on-chain accounting and no revert. This matches "Critical: direct theft of shielded or in-flight user funds" if in-flight/leftover Emporium funds or third-party approvals held by Emporium can be found in practice. The bug is repeatable for as long as such approvals/leftover balances exist, and each `emporiumMessage` can only be used once (`usedMessages` mapping) but the attacker can mint arbitrarily many unique `emporiumMessage` values costing only gas.

### Likelihood Explanation
- No privileged role or note ownership is required: the attacker needs no funds, no valid Merkle leaf, and no legitimate signature — the Min-circuit proof requires only knowledge of an arbitrary `messageSeed`.
- The attacker fully controls `externalActionData.externalActionMetadata` (the `EmporiumStack`), `emporiumMessage`, and the empty token array.
- The exploit's real-world value depends entirely on Emporium holding drainable funds or being the beneficiary of a standing third-party approval at the time of the attack — this is an external precondition not verifiable purely from the reachable contract code shown here.
- Cost to the attacker is a single transaction plus proof generation for the trivial Min circuit.

### Recommendation
- Do not allow the Min-circuit path to reach `EmporiumUpgradeable.runAction` with a non-empty `stack.ops` when `signerAddress == address(0)`; require `stack.ops.length == 0` (or disallow the min path for Emporium entirely) unless a valid signature (or some other authorization binding `msg.sender`/proof to the ops) is present.
- Make `verifyWallet` reject the `signerAddress == address(0)` bypass unless the caller is provably the depositor of the exact assets being moved (e.g., require `erc20TokenAddresses.length > 0` and re-enable the balance-based accounting, or require the Min circuit to still constrain `rootHashHinkal`/nullifiers to prove note ownership).
- Ensure the balance-accounting loop in `runAction` cannot be trivially neutered by supplying an empty `erc20TokenAddresses` array; consider tracking Emporium's balances via an allow-listed set of tokens or requiring `dimensions.tokenNumber > 0` for any Emporium action containing calls.

### Proof of Concept
Foundry outline (fork or local deployment):
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, and register Emporium in `externalActionMap[HINKAL_EMPORIUM_ACTION_ID]`.
2. Simulate a precondition: have a "victim" ERC20 token grant an allowance to the Emporium contract address (`token.approve(emporiumAddress, amount)` from victim), representing a standing approval left over from a prior legitimate flow.
3. As an unprivileged attacker (no deposits, no notes), build `CircomData` with:
   - `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`
   - `erc20TokenAddresses = []`, `amountChanges = []`, `onChainCreation = []`, `inputNullifiers = []`, `outCommitments = []`, `encryptedOutputs = []`
   - `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({v:0,r:0,s:0, signerAddress: address(0), ops: [EmporiumOperation({endpoint: address(victimToken), invokeWallet:false, value:0, callData: abi.encodeCall(IERC20.transferFrom,(victim, attacker, amount))})], maxFee:0, deadline: block.timestamp+1}))`
   - `emporiumMessage`, `calldataHash` computed correctly per `CircomDataBuilder.getHashedCalldata`.
4. Generate a trivially valid Min-circuit proof for `message == Poseidon(messageSeed)`.
5. Call `Hinkal.transact(...)`.
6. Assert equality broken: `balancesBefore.length == 0 == balancesAfter.length` (no accounting performed) while `victimToken.balanceOf(attacker)` increased by `amount` and `victimToken.balanceOf(victim)` decreased by `amount` — i.e., value left the system with zero entries in `balancesBefore`/`balancesAfter`.
7. Assert the transaction does not revert with `BalanceChangeShouldBePositive` (proving the guard never triggers because the token array is empty).

Note: step 2 (the standing-approval precondition) needs to be validated against actual production usage patterns to confirm this attack has a real fund source; this was not verifiable purely from the indexed contract code.

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

**File:** contracts/Hinkal.sol (L57-64)
```text
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-160)
```text
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

**File:** contracts/HinkalHelper.sol (L64-90)
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
```

**File:** contracts/HinkalHelper.sol (L173-200)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

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

**File:** contracts/HinkalHelper.sol (L220-225)
```text

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```
