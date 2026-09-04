### Title
Emporium raw op-call forwarding lets an attacker replay forged `CircomData` into `DepositOnChainUtxosExternalAction` to steal from arbitrary victims - (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` executes `op.endpoint.call{value: op.value}(op.callData)` for each entry in `stack.ops` with fully attacker-controlled `callData` [1](#0-0) . Because Emporium is a registered `allowedRecipient` on `DepositOnChainUtxosExternalAction`, the attacker can encode `op.callData` as a direct call to `DepositOnChainUtxosExternalAction.runAction(forgedCircomData, [0,...])`, where `forgedCircomData.originalSender` is set to any victim address. That inner `CircomData` struct is never checked against the proof-verified outer `circomData`, against `msg.sender` of `Hinkal.transact`, or against `HinkalHelper.performHinkalChecks`'s `originalSender == sender` equality, because that check is only performed once, on the outer struct, before `Hinkal.transact` calls `verifyProof` [2](#0-1) [3](#0-2) .

### Finding Description
The equality that should hold, but is broken:
`forgedCircomData_1.originalSender == forgedCircomData_2.originalSender == outerCircomData.originalSender == msg.sender-of-verified-proof`.

After the attack, `forgedCircomData_1.originalSender = victim1`, `forgedCircomData_2.originalSender = victim2`, while the *only* proof ever verified in the transaction belongs to the attacker's own `outerCircomData` (`Hinkal.transact` calls `verifyProof` exactly once, before any external action executes) [4](#0-3) .

Call path:
1. Attacker calls `Hinkal.transact` with a valid proof for their own (trivial) UTXO operation, `externalActionId` pointing to `EmporiumUpgradeable`, and `externalActionData.externalActionMetadata = abi.encode(EmporiumStack)`.
2. `Hinkal.transact` → `performHinkalChecks` validates only the outer `circomData.originalSender == msg.sender` [5](#0-4) , verifies the single proof, then calls `_externalTransact` → `EmporiumUpgradeable.runAction` [6](#0-5) .
3. Inside `EmporiumUpgradeable.runAction`, the attacker sets `stack.signerAddress = address(0)` (skipping the EIP-712 signature check entirely, `verifyWallet` only records `usedMessages` in that branch) [7](#0-6) , and supplies two `EmporiumOperation` entries with `invokeWallet=false`, `endpoint = DepositOnChainUtxosExternalAction`, and `callData` = ABI-encoded calls to `runAction` carrying two independently-forged `CircomData` structs (`originalSender=victim1`/`victim2`, `erc20TokenAddresses=[T1]`/`[T2]`, `externalActionMetadata = abi.encode(utxoAmounts)`).
4. Each raw `.call` reaches `DepositOnChainUtxosExternalAction.runAction`, where `msg.sender` is `EmporiumUpgradeable` (an allowed recipient), so `onlyAllowedRecipient` passes [8](#0-7) . The function then does `transferERC20TokenFrom(tokenAddress, userAddress=victim, msg.sender=Emporium, tokenTotal)` using the victim's pre-existing ERC20 approval to `DepositOnChainUtxosExternalAction` [9](#0-8) . `deltaAmounts[i]` is forced to `0` by a `require`, which is trivially satisfiable since the attacker supplies both `circomData` and `deltaAmounts` inside the raw call.
5. Both victims' tokens land in the Emporium contract's balance. Back in `EmporiumUpgradeable.runAction`, the balance-delta bookkeeping (`balancesAfter - balancesBefore`, using the *outer*, attacker-controlled `circomData.erc20TokenAddresses = [T1, T2]`) treats this increase as legitimate emporium output and sweeps it to `msg.sender` (the attacker) via `handleOut` → `transferERC20TokenOrETH` [10](#0-9) .

Root cause: `runAction(CircomData, int256[])` on external actions is designed to only ever be invoked with the single `circomData` struct that was verified by the ZK proof for that transaction (enforced implicitly by `Hinkal._externalTransact` always passing the same struct it just checked) [11](#0-10) . `EmporiumUpgradeable.runAction`'s stateless-interaction branch breaks this invariant by allowing arbitrary raw calldata to be forwarded to *any* endpoint, including other `IExternalActionV2` implementations that trust their caller's `onlyAllowedRecipient` status rather than re-verifying a proof. No component ever checks that a nested/forged `CircomData.originalSender` matches the actual token owner authorizing the transfer, nor is it bound to the single proof verified in `Hinkal.transact`.

### Impact Explanation
Direct theft of shielded/unshielded ERC20 funds from any number of victims who granted allowance to `DepositOnChainUtxosExternalAction`, in a single transaction backed by only one (attacker's own) valid proof. This matches Critical severity: "direct theft of shielded or in-flight user funds" and "proof or nullifier verification bypass" — the proof only covers the attacker's own trivial operation, yet the actual value transfer is dictated by unconstrained, forged data. The attack is repeatable against every victim with an outstanding approval and scales to N victims per transaction (bounded only by `stack.ops.length` and gas).

### Likelihood Explanation
Preconditions are realistic and already assumed in the question: victims must have approved `DepositOnChainUtxosExternalAction` (a normal, expected precondition for using that action legitimately) and `EmporiumUpgradeable` must be a registered allowed recipient on it (also a normal deployment configuration, since Emporium is meant to compose with other actions). The attacker needs no special privileges — only the ability to submit their own valid proof for a trivial/no-op UTXO operation and craft arbitrary `EmporiumStack`/`EmporiumOperation` bytes, which the question's threat model explicitly grants. Cost is a single transaction; feasibility is high since `stack.signerAddress = address(0)` bypasses signature verification for the raw-call branch entirely.

### Recommendation
Do not allow `EmporiumUpgradeable`'s raw `op.endpoint.call(op.callData)` path to target other `IExternalActionV2`/`onlyAllowedRecipient`-gated contracts with attacker-supplied `CircomData`. Either (a) maintain an explicit denylist/allowlist of callable selectors and endpoints that excludes all `runAction`-style entry points of registered external actions, or (b) require that any `CircomData` passed into a nested `runAction` call be structurally identical (or cryptographically bound via the same proof/public-input set) to the outer, proof-verified `circomData`, e.g. by having `DepositOnChainUtxosExternalAction` (and all `IExternalActionV2` implementations) also verify `originalSender` came from a value bound to the currently verified proof rather than trusting `onlyAllowedRecipient` alone.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (registered as an external action and as an allowed recipient on `DepositOnChainUtxosExternalAction`), and `DepositOnChainUtxosExternalAction`.
2. Create two victim EOAs, mint `T1`/`T2` to each, have each victim call `T1.approve(depositAction, type(uint256).max)` / `T2.approve(depositAction, type(uint256).max)`.
3. As the attacker, build a valid ZK proof for a trivial/no-op Hinkal transaction whose `circomData.externalActionData.externalActionId` = Emporium's id and `externalActionMetadata` encodes an `EmporiumStack` with `signerAddress = address(0)` and two `EmporiumOperation` entries:
   - `endpoint = depositAction`, `callData = abi.encodeCall(IExternalActionV2.runAction, (forgedCircomData1, [int256(0)]))` where `forgedCircomData1.originalSender = victim1`, `erc20TokenAddresses = [T1]`, metadata encodes `utxoAmounts = [[A1]]`.
   - same for `victim2`/`T2`/`A2`.
4. Call `Hinkal.transact(a, b, c, dimensions, circomData)` once.
5. Assert: `T1.balanceOf(victim1)` dropped by `A1`, `T2.balanceOf(victim2)` dropped by `A2`, attacker's tracked UTXO/balance increased accordingly, and that `verifyProof`/the verifier mock was invoked exactly once for the whole transaction (mock a counting verifier to assert call count == 1), demonstrating the equality `forgedCircomData1.originalSender != forgedCircomData2.originalSender != outerCircomData.originalSender` while only one proof was ever checked.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L120-184)
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

    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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

**File:** contracts/HinkalHelper.sol (L208-219)
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
```

**File:** contracts/Hinkal.sol (L30-65)
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

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L16-22)
```text
    modifier onlyAllowedRecipient() {
        require(
            isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L74-82)
```text

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```
