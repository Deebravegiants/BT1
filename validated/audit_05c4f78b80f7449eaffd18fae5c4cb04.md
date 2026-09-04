### Title
Empty-token-array Emporium action bypasses balance accounting, allowing unauthenticated arbitrary calls from `address(Emporium)` - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When `circomData.erc20TokenAddresses.length == 0`, `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin`, whose only public inputs are `emporiumMessage`, `timeStamp`, `calldataHash` and whose backing circuit `MainEVMCircuitMin` only constrains `message == Poseidon(1)([messageSeed])` — no root, nullifier, or key ownership signal is ever checked. Combined with `EmporiumUpgradeable.runAction`, whose `verifyWallet` skips all authorization when `stack.signerAddress == address(0)`, and whose balance-diff loop is bounded by `circomData.erc20TokenAddresses` (empty), an attacker can force `Emporium` to make an arbitrary low-level call to any endpoint, with `msg.sender == address(Emporium)`, that is entirely unaccounted for by any balance check.

### Finding Description
The broken equality: `assets_moved_by_Emporium_call` (bounded only by what `op.endpoint.call{value: op.value}(op.callData)` can move while `msg.sender == address(Emporium)`) is **not** bounded by `assets_counted_in_balance_loop` (`circomData.erc20TokenAddresses`, which is empty in this path).

Path:
1. `Hinkal.transact` → `hinkalHelper.performHinkalChecks` → `dimensionsCheck` accepts `tokenNumber == 0` trivially (all length checks become `0 == 0`) [1](#0-0) , then `CircomDataBuilder.formInputForCircom` routes to `formInputEmporiumMin` because `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0` [2](#0-1) .
2. The circuit `MainEVMCircuitMin` only constrains `message <== Poseidon(1)([messageSeed])`, with `outTimeStamp` and `calldataHash` passed through unconstrained [3](#0-2) . The attacker freely picks `messageSeed`, computes `message`, sets `circomData.emporiumMessage = message`, and generates a trivially valid proof. `calldataHash` is separately pinned to the attacker's own calldata via `getHashedCalldata` check in `performHinkalChecks`, which the attacker fully controls since it's their own transaction [4](#0-3) .
3. `Hinkal.sol.transact` top-level balance loop is also indexed by `circomData.erc20TokenAddresses` (empty), so no accounting happens there either [5](#0-4) .
4. `EmporiumUpgradeable.runAction` decodes `EmporiumStack{signerAddress: address(0), ops: [...]}` from attacker-controlled `externalActionMetadata`. `verifyWallet` marks `usedMessages[emporiumMessage] = true` and returns immediately since `stack.signerAddress == address(0)`, performing **no** signature/authorization check [6](#0-5) .
5. The op loop then executes `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == address(Emporium)` for an attacker-chosen `endpoint`/`callData` [7](#0-6) .
6. `balancesBefore`/`balancesAfter` are computed over the empty `erc20TokenAddresses` array, so the subsequent loop that would revert on `balanceChange < 0` (line 142, `BalanceChangeShouldBePositive`) never executes for any token actually touched by the arbitrary call [8](#0-7) .

Notably, the code's own comment ("the only case when balanceChange can be < 0, when there were some funds on emporium before the call") confirms `Emporium` is expected to sometimes hold pre-existing balance/dust between transactions — exactly the asset this bypass lets an attacker sweep via any endpoint/calldata of their choosing, with `Emporium`'s identity as `msg.sender`.

None of the existing guards (`dimensionsCheck`, `verifyProof`/`buildVerifierId`, `rootHashExists`, the balance loops, `onlyAllowedRecipient`, `nonReentrant`) constrain this path, because they are all either satisfied trivially by zero-length arrays or indexed by the very array the attacker chose to leave empty.

### Impact Explanation
Any ETH or ERC20 balance sitting at `address(Emporium)` (dust from prior multi-hop swaps, ETH sent via its `receive()` fallback, or any allowance a third-party contract has granted to `Emporium`) can be moved out via an arbitrary call chosen entirely by an unprivileged attacker, with no proof of ownership, no signature, and no balance accounting. This is theft of protocol/pooled funds executed via a call the wallet owner/prover never authorized, and is repeatable per unique `emporiumMessage` (trivial and cheap to generate, since the circuit is a single Poseidon hash).

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: `HINKAL_EMPORIUM_ACTION_ID` and `Emporium`'s registered address are public deployment facts; the attacker needs only to generate a `MainEVMCircuitMin` proof (no tree/nullifier state required) and craft `EmporiumStack` with `signerAddress = address(0)`. Cost is a single cheap proof generation and gas; the attack is repeatable indefinitely with fresh `emporiumMessage` values (the only per-call constraint is `usedMessages` uniqueness). The attack's practical yield depends on `Emporium` holding exploitable balance/allowances at the time of attack, but the codebase's own logic anticipates and handles this exact scenario ("funds on emporium before the call"), so it is a realistic and reachable state, not a purely theoretical one.

### Recommendation
Do not allow `formInputEmporiumMin`/min-circuit dispatch to bypass balance accounting for the ops loop. At minimum:
- Reject `HINKAL_EMPORIUM_ACTION_ID` calls with `erc20TokenAddresses.length == 0` unless `stack.signerAddress != address(0)` (i.e., forbid the unauthenticated/"stateless, unsigned" combination from executing arbitrary `op.endpoint.call`).
- Alternatively, require `verifyWallet` to always enforce a valid signature/authorization regardless of `erc20TokenAddresses.length`, decoupling "min circuit" gas savings from bypassing wallet/signature verification.
- Ensure `Emporium` never retains sweepable balance between transactions (sweep to Hinkal or revert on any residual balance at end of `runAction`, even when `erc20TokenAddresses` is empty).

### Proof of Concept
Foundry fork test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, and register `mainEVMCircuitMin0v4` verifier for the zero-dimension `buildVerifierId`.
2. Fund `address(Emporium)` with ERC20 tokens/ETH via a legitimate multi-hop swap flow that leaves dust (or directly via `receive()`), simulating realistic residual balance.
3. Off-chain: pick `messageSeed`, compute `message = Poseidon(1)([messageSeed])`, generate a valid `MainEVMCircuitMin` proof with `emporiumMessage = message`.
4. Craft `circomData` with `erc20TokenAddresses = []`, `externalActionData = {externalAddress: Emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: attackerContract, invokeWallet: false, value: 0, callData: <drain calldata>}]})}`.
5. Call `Hinkal.transact` with this proof/data as an unprivileged EOA.
6. Assert: `balancesBefore == balancesAfter` for the (empty) `circomData.erc20TokenAddresses` array (no revert triggered), while `attackerContract`'s or `attacker`'s actual token/ETH balance increases and `Emporium`'s real balance decreases — demonstrating `assets_moved_by_Emporium_call != assets_counted_in_balance_loop`.

### Citations

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

**File:** contracts/HinkalHelper.sol (L204-236)
```text
    ///@notice make performance checks for transactions
    ///@dev Check if transacaction is valid before making it
    ///@param circomData circom data
    ///@return inputForCircom
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

**File:** contracts/Hinkal.sol (L76-90)
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
