### Title
Emporium `runAction` allows unauthenticated, unbacked arbitrary calls via the "min" (zero-token) proof path - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
`Hinkal.transact()` supports a special "Emporium-min" input path (`formInputEmporiumMin`) that is used whenever `externalActionData.externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0` [1](#0-0) . The circuit bound to this path, `MainEVMCircuitMin`, only proves knowledge of a `messageSeed` that hashes (via Poseidon) to some `message` output — it contains no nullifier, no commitment, no root-hash and no ownership constraint whatsoever [2](#0-1) . Because `erc20TokenAddresses.length == 0`, `EmporiumUpgradeable.runAction`'s post-call balance-conservation loop iterates zero times, so no balance check is ever performed [3](#0-2) . Combined with `EmporiumOperation`'s CASE 2 "stateless" branch, which executes `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract whenever `stack.signerAddress == address(0)` (no EIP-712 signature check is performed in that case — `verifyWallet` just returns early) [4](#0-3) [5](#0-4) , this lets **any unprivileged EOA** get the Emporium contract to send arbitrary crafted calldata to an arbitrary `endpoint`, with Emporium as `msg.sender`, while proving nothing more than knowledge of a self-chosen `messageSeed` — exactly the "notification/message with arbitrary payload, no funds moved" pattern described in the external report.

### Finding Description
Normally `runAction` enforces a balance equality: for every token in `circomData.erc20TokenAddresses`, `balancesAfter[i] - balancesBefore[i] - deltaAmountChanges[i] >= 0`, which prevents Emporium from being used to withdraw value that wasn't actually deposited [6](#0-5) . This equality is the on-chain analog of the vault's "tokens received before message sent" check referenced in the report.

The `HinkalHelper.performHinkalChecks` → `CircomDataBuilder.formInputForCircom` dispatch routes to `formInputEmporiumMin` whenever the caller sets `erc20TokenAddresses` to an empty array and `externalActionId == HINKAL_EMPORIUM_ACTION_ID` [7](#0-6) . In this path the "equality" that should tie the proof to spent value (root hash membership, nullifiers, commitments) simply does not exist in the circuit — `MainEVMCircuitMin` has no such signals at all, it only outputs `Poseidon(messageSeed)` [2](#0-1) . `Hinkal.transact()` still performs `rootHashExists(circomData.rootHashHinkal, ...)`, but with zero declared tokens and no nullifiers required by the circuit, an attacker can freely reuse any historical valid root without proving ownership of any UTXO in it [8](#0-7) .

Once inside `_externalTransact`/`runAction`, since `erc20TokenAddresses.length == 0`, no per-token balance delta is ever computed or enforced [3](#0-2) , and `verifyWallet` with `stack.signerAddress == address(0)` performs no signature check on `stack.ops`, only marking `emporiumMessage` as used (a value fully chosen by the attacker in the same call, so trivially fresh) [4](#0-3) . The loop over `stack.ops` then performs `op.endpoint.call{value: op.value}(op.callData)` for every op that isn't `invokeWallet`, with only a selector-based check to prevent calling `callHinkalWallet`/`doSendToRelay` directly on a wallet [9](#0-8) .

This breaks the equality "value moved by Hinkal/Emporium must be counted in the balance equation": the entire balance-check machinery that exists specifically to stop `runAction` from being used as a free arbitrary-message relay is bypassable simply by choosing `erc20TokenAddresses = []`, `circomData.calldataHash`-matching metadata, and a trivial min-circuit proof that requires no real shielded funds or signature.

### Impact Explanation
Any unprivileged EOA can force the `Emporium` contract to execute arbitrary external calls (`op.endpoint.call(op.callData)`) with `Emporium` as `msg.sender`, without owning any shielded UTXO, without any EIP-712 signature, and without any balance check — exactly the "arbitrary message with the vault's identity, without transferring tokens" bug class from the external report. This can be used to:
- Impersonate the Emporium contract to any third-party protocol that has granted Emporium an approval/allowance or otherwise trusts `msg.sender == Emporium` (e.g., call `transferFrom` using an existing allowance, or trigger privileged callback logic keyed on Emporium's address), moving/misappropriating assets Emporium controls or is trusted with.
- Drain any ERC20/ETH dust that legitimately or illegitimately resides in the Emporium contract (e.g. from failed prior ops, rounding, or other users' in-flight funds), since none of that is protected by a balance check when `erc20TokenAddresses` is empty.

This is unauthorized execution of calls/movement of assets that were never authorized by a prover or signer, satisfying the High/Critical bar ("executing calls or moving assets a wallet owner or prover never authorized," and potentially "theft ... of protocol/relay fees" or shielded funds sitting in Emporium).

### Likelihood Explanation
High. The path requires no privileged role, no relayer collusion, and no real shielded balance — only crafting `circomData` with `erc20TokenAddresses = []`, a self-chosen `messageSeed`/`emporiumMessage`, `stack.signerAddress = address(0)`, and an `EmporiumOperation` with the desired `endpoint`/`callData`, then generating a trivial proof for `MainEVMCircuitMin`. All of the pieces (the min-circuit dispatch, the zero-signature branch, and the empty-array balance loop) are independently reachable through the public `transact()` entrypoint.

### Recommendation
- Reject `externalActionId == HINKAL_EMPORIUM_ACTION_ID` with `erc20TokenAddresses.length == 0` unless `stack.signerAddress != address(0)` and a valid EIP-712 signature over `stack.ops` is present, so the "min" path can never execute CASE 2 stateless calls unauthenticated.
- Alternatively, disallow CASE 2 (`op.endpoint.call`) entirely when `erc20TokenAddresses.length == 0`, or require that every `op.endpoint`/`callData` be covered by a signature check (not only when `signerAddress != 0`).
- Ensure the balance-conservation loop cannot be trivially bypassed by supplying an empty token array — e.g., require `erc20TokenAddresses.length > 0` whenever `stack.ops` contains a raw external call, or track/restrict which contracts Emporium is allowed to call.

### Proof of Concept
1. Attacker (no shielded balance required) calls `Hinkal.transact()` with:
   - `dimensions` / `circomData.erc20TokenAddresses = []`
   - `circomData.externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`
   - `circomData.externalActionData.externalActionMetadata = abi.encode(EmporiumStack({ signerAddress: address(0), ops: [EmporiumOperation({endpoint: <victimOrAllowanceHolder>, invokeWallet: false, value: 0, callData: <arbitrary calldata, e.g. transferFrom/approve-abusing call>})], maxFee: 0, deadline: 0 }))`
   - a proof generated for `MainEVMCircuitMin` using an attacker-chosen `messageSeed` (no ownership of funds needed) and `circomData.calldataHash` matching `getHashedCalldata(circomData)`.
2. `Hinkal.transact()` verifies the trivial proof and existing root hash, then calls `_externalTransact` → `EmporiumUpgradeable.runAction` [10](#0-9) .
3. `runAction`: `verifyWallet` returns immediately (no signature check, `signerAddress == 0`); the ops loop executes `op.endpoint.call(op.callData)` with `msg.sender == Emporium`; post-loop the balance loop is a no-op because `erc20TokenAddresses.length == 0` [11](#0-10) .
4. The arbitrary call is executed as Emporium with zero funds ever moved through Hinkal's accounting, matching the report's "arbitrary message with no token transfer" bug class.

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

**File:** circuits/MainEVMCircuitMin.circom (L1-17)
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

**File:** contracts/Hinkal.sol (L56-64)
```text
            );
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
