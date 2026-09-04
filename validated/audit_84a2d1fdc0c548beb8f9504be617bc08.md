### Title
Emporium Min-proof path lets any attacker execute unaccounted arbitrary calls from Emporium's identity, stealing funds/approvals it holds - (File: `contracts/CircomDataBuilder.sol` / `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, which proves only `message == Poseidon(messageSeed)`, `timeStamp` and `calldataHash` [1](#0-0) . With `erc20TokenAddresses` empty, `EmporiumUpgradeable.runAction`'s balance-accounting loop (`balancesBefore`/`balancesAfter`) is vacuously empty, while the attacker-supplied `EmporiumStack` with `signerAddress == 0` still executes arbitrary `op.endpoint.call{value: op.value}(op.callData)` calls with zero signature verification and zero balance reconciliation [2](#0-1) .

### Finding Description
The invariant that should hold is: *assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`*. `dimensionsCheck` forces `circomData.amountChanges.length == circomData.erc20TokenAddresses.length == dimensions.tokenNumber` [3](#0-2) , so choosing `erc20TokenAddresses = []` makes `amountChanges`, `deltaAmountChanges`, `balancesBefore`, and `balancesAfter` all zero-length. The min-circuit public input vector formed by `formInputEmporiumMin` contains only `emporiumMessage`, `timeStamp`, and `calldataHash` — it does not constrain `amountChanges`, `rootHashHinkal`, `inputNullifiers`, `outCommitments`, or ownership of any UTXO/funds [4](#0-3) . Since `emporiumMessage` is fully attacker-chosen (any Poseidon preimage they know), and `getHashedCalldata`/`calldataHash` is simply matched against attacker-supplied calldata (a plain equality, not an independent identity check) [5](#0-4) , the attacker can freely craft `circomData.externalActionData.externalActionMetadata` as any `EmporiumStack`.

Critically, `EmporiumUpgradeable.verifyWallet` performs **no signature check at all** when `stack.signerAddress == address(0)` — it just marks `emporiumMessage` used and returns [6](#0-5) . In that "Stateless Interaction" branch, `runAction` executes `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract's own identity/msg.sender context, with the only restriction being that the calldata selector isn't `callHinkalWallet`/`doSendToRelay` [7](#0-6) . Because `erc20TokenAddresses` is empty, the post-call reconciliation loop (`balanceChange` computation and `BalanceChangeShouldBePositive` revert) never executes for any token the op actually touches [8](#0-7) .

Exploit flow: attacker calls `Hinkal.transact` with `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, and an `EmporiumStack{signerAddress: address(0), ops: [{endpoint: <token or victim-approved contract>, callData: transferFrom(victim, attacker, amount) or transfer(attacker, amount)}]}`. They generate a trivial min-circuit proof (self-chosen `messageSeed`). `performHinkalChecks` passes (calldata hash matches itself, dimensions match zero-length arrays), `verifyProof` passes (min circuit only checks the Poseidon relation), `rootHashExists` is irrelevant to this path since no nullifiers/roots are used. `_externalTransact` builds a zero-length `deltaAmountChanges` and calls `EmporiumUpgradeable.runAction`, which executes the attacker's call from Emporium's own address — capable of draining any ERC20 balance Emporium holds or pulling tokens via any standing `approve(Emporium, amount)` a victim previously granted — with no accounting check preventing or even detecting the outflow.

### Impact Explanation
This allows an unprivileged attacker to direct the Emporium contract to execute arbitrary calls that move value (ERC20 transfers, `transferFrom` against standing approvals, or ETH via `op.value`) while completely bypassing the balance-accounting invariant that is supposed to gate every asset movement in `runAction`. Any funds held by Emporium (leftover balances from other users' shielded operations, or tokens for which any account has approved Emporium as spender) can be stolen directly. This matches **Critical: direct theft of shielded or in-flight user funds**, and is repeatable per distinct `emporiumMessage`/token target as long as Emporium holds exploitable balance or approvals.

### Likelihood Explanation
No privileged role is required. The attacker needs only: (1) ability to call `Hinkal.transact` (any EOA), (2) a self-generated min-circuit proof (trivial, since they choose the Poseidon preimage), and (3) Emporium to hold some balance or a standing token approval from any account. Given Emporium is designed to hold/move funds on behalf of users during its `ops` execution, non-zero balances/approvals are a realistic and likely operational state, making this readily exploitable.

### Recommendation
Do not allow the zero-accounting fast path to authorize unrestricted, unsigned external calls. Specifically: require `stack.signerAddress != address(0)` (i.e., mandatory signature verification) whenever `erc20TokenAddresses.length == 0`, or reject the min-proof path entirely unless `stack.ops.length == 0` / ops are provably side-effect-free. Alternatively, always require `erc20TokenAddresses` to include every token/ETH touched by `ops` so the balance-before/after reconciliation cannot be bypassed by submitting an empty token array.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as a registered external action, allowed recipient = Hinkal), a mock ERC20 `TOKEN`.
2. Fund `Emporium` with `TOKEN` (e.g., via a legitimate prior transact) or have a third-party victim call `TOKEN.approve(EmporiumAddress, X)` directly.
3. Attacker crafts `circomData` with `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, `amountChanges = []`, `externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: TOKEN, invokeWallet: false, value: 0, callData: abi.encodeCall(TOKEN.transfer, (attacker, X))})], maxFee: 0, deadline: type(uint256).max}))`.
4. Generate a min-circuit proof for `emporiumMessage = Poseidon(attackerChosenSeed)` (locally, using snarkjs with the circuit's own trusted setup) and set `calldataHash = getHashedCalldata(circomData)`.
5. Call `Hinkal.transact(a, b, c, dimensions{tokenNumber:0,...}, circomData)`.
6. Assert: `TOKEN.balanceOf(attacker)` increases by `X`, and `TOKEN.balanceOf(Emporium)` decreases by `X` — i.e., `balancesBefore == balancesAfter` (both empty arrays, invariant vacuously "held") while actual on-chain balances diverge by `X`, proving the equality "assets moved == assets accounted" is broken.

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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```
