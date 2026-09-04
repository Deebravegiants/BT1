### Title
Emporium "Min" flow (`erc20TokenAddresses.length == 0`) lets ops drain Emporium's native ETH balance with zero on-chain accounting - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When `circomData.externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `circomData.erc20TokenAddresses.length == 0` ("Emporium Min"), `CircomDataBuilder.formInputEmporiumMin` produces a public-input vector containing only `emporiumMessage`, `timeStamp`, `calldataHash` — no `rootHashHinkal`, no nullifiers, no `amountChanges`. Inside `EmporiumUpgradeable.runAction`, the balance-safety loop (`balancesBefore`/`balancesAfter`/`balanceChange < 0` revert) iterates over `circomData.erc20TokenAddresses`, which is empty, so it never executes — meaning any ETH the ops move out of the Emporium contract via `op.endpoint.call{value: op.value}(op.callData)` (CASE 2, stateless) is completely unchecked.

### Finding Description
The claimed equality is:
`declared tokens leaving (sum of |amountChanges| routed out of Emporium) == actual ETH leaving Emporium's own balance (sum of op.value across ops)`

Trace:
- `dimensionsCheck` (`contracts/HinkalHelper.sol:64-171`) only requires `erc20TokenAddresses.length == amountChanges.length == dimensions.tokenNumber`; `tokenNumber = 0` is a legal, attacker-chosen dimension. [1](#0-0) 
- `CircomDataBuilder.formInputForCircom`/`formInputEmporiumMin` explicitly branches into a minimal public-input set (no root, no nullifiers, no amountChanges) exactly when `erc20TokenAddresses.length == 0`. [2](#0-1) 
- In `EmporiumUpgradeable.runAction`, `balancesBefore`/`balancesAfter` are computed via `getBalancesForArray(circomData.erc20TokenAddresses)`, and the reconciliation loop that reverts on `balanceChange < 0` is bounded by `circomData.erc20TokenAddresses.length`. [3](#0-2) 
- With `erc20TokenAddresses.length == 0`, this loop body never runs — there is no equality check at all, not even a broken one; the guard is simply absent.
- The ops themselves execute unconditionally before that loop: for `stack.signerAddress == address(0)`, `verifyWallet` only checks/marks `usedMessages[circomData.emporiumMessage]` and returns immediately without any signature check on `stack.ops`. [4](#0-3) 
- CASE 2 (`op.invokeWallet == false` or no signer) executes `op.endpoint.call{value: op.value}(op.callData)` directly against attacker-supplied `endpoint`/`callData`/`value`, moving ETH out of `address(this)` (Emporium's own balance). [5](#0-4) 
- `calldataHash` is only a self-consistency hash the attacker computes themselves over their own `circomData` (`getHashedCalldata`, `contracts/CircomDataBuilder.sol:10-54`, checked in `performHinkalChecks` at `contracts/HinkalHelper.sol:221-225`); it does not constrain the *content* of `stack.ops` against anything the attacker doesn't already control.

Attacker's exact call: submit a Hinkal `transact` with `circomData.erc20TokenAddresses = []`, `amountChanges = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata = abi.encode(EmporiumStack{signerAddress: address(0), ops: [ {endpoint: attacker1, invokeWallet:false, value: v1, callData: ""}, {endpoint: attacker2, ..., value: v2}, ... ] })`, plus a valid proof for the "Min" circuit variant (whose public inputs are only `emporiumMessage/timeStamp/calldataHash`, none of which constrain `stack.ops`). `runAction` executes every op, sending `v1, v2, ...` ETH out of Emporium's balance to attacker-controlled addresses, and the balance-check loop that would otherwise revert on unexplained outflow never runs because `erc20TokenAddresses.length == 0`. Splitting one large `op.value` into several smaller ops across several addresses (as the question suggests) does not change the exploit — it only obscures it in event logs, since there is no accounting to fool in the first place.

Existing guards do not prevent this: `performHinkalChecks`/`dimensionsCheck` accept `tokenNumber = 0` by design (this is the documented "Emporium Min" fast path per `formInputEmporiumMin`), `verifyProof` for the Min circuit only authenticates `emporiumMessage/timeStamp/calldataHash`, and `insertNullifiers`/root checks are skipped entirely for this path since `inputNullifiers` is empty.

### Impact Explanation
Direct theft of native ETH sitting in the `EmporiumUpgradeable` contract — which can include pooled/in-flight shielded funds belonging to other users awaiting sweep-out via `handleOut`, or protocol/relay funds. The attacker can repeat this every time Emporium holds a nonzero ETH balance, draining it fully in one or many transactions with no cap enforced by the contract logic (only bounded by actual balance and gas). This matches Critical severity: direct theft of shielded/in-flight user funds via a code path where the proof/accounting never constrains the actual value moved.

### Likelihood Explanation
Preconditions: `EmporiumUpgradeable` must hold a nonzero ETH balance (e.g., ETH deposited for use in ops but not yet swept, or leftover from a prior op that reverted mid-flow, or ETH sent to the contract's `receive()`). The attacker needs no privileged role — any EOA can call `transact` with a self-crafted `circomData` in "Emporium Min" mode and a proof for that circuit, since none of the Min circuit's public inputs constrain the op list. Cost is just gas plus proof generation, which is cheap and fully within attacker's control (self-issued nullifier-free proof). This is directly repeatable as long as Emporium's balance is nonzero.

### Recommendation
Remove the zero-token "Min" fast path's exemption from balance accounting, or explicitly disallow using `externalActionMetadata` (i.e., `EmporiumOperation[].value`) to move native ETH when `erc20TokenAddresses.length == 0`. At minimum, always include `address(0)` (native ETH) balance tracking in `EmporiumUpgradeable.runAction` regardless of `erc20TokenAddresses` length, and require any nonzero `op.value` total to be reconciled against a corresponding entry in `amountChanges`/`erc20TokenAddresses`, reverting on unexplained outflow even when the caller supplies zero-length arrays.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, fund it directly with ETH (simulate pooled/leftover balance), record `preBalance = address(emporium).balance`.
2. Craft `EmporiumStack{ signerAddress: address(0), ops: [ {endpoint: attacker1, invokeWallet:false, value: v1, callData: ""}, {endpoint: attacker2, invokeWallet:false, value: v2, callData: ""} ] }` with `v1 + v2 == preBalance`.
3. Build `circomData` with `erc20TokenAddresses = []`, `amountChanges = []`, `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `externalActionMetadata = abi.encode(stack)`, self-computed `calldataHash`.
4. Call `Hinkal.transact` (or directly `EmporiumUpgradeable.runAction` if testing in isolation with `onlyAllowedRecipient` mocked) with a valid Min-circuit proof.
5. Assert `attacker1.balance + attacker2.balance == preBalance` (full drain) and assert `circomData.amountChanges` sums to `0` (i.e., `sum(abs(amountChanges)) == 0`), proving the equality `declared outflow (0) != actual outflow (preBalance)`.

### Citations

**File:** contracts/HinkalHelper.sol (L64-76)
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
