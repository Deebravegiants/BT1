### Title
Unbounded theft of victim's ERC20 allowance via forged `CircomData` nested-call into `DepositOnChainUtxosExternalAction.runAction` - (File: contracts/external-actions/DepositOnChainUtxosExternalAction.sol)

### Summary
`DepositOnChainUtxosExternalAction.runAction` is gated only by `onlyAllowedRecipient`, a plain `mapping(address=>bool)` with no binding to the specific `CircomData` that was proof-verified by `Hinkal.transact`. Any allowed-recipient contract that itself performs an attacker-controlled low-level call (e.g. Emporium's stateless `op.endpoint.call(op.callData)`) can invoke `runAction` directly with a fully forged `CircomData`, letting the attacker set `circomData.originalSender` to any victim and `utxoAmounts` to any total, draining the victim's entire ERC20 allowance to `DepositOnChainUtxosExternalAction` in one transaction.

### Finding Description
The claimed equality: "every call to `DepositOnChainUtxosExternalAction.runAction` operates on the same `CircomData` that was verified by `Hinkal.verifyProof`/`performHinkalChecks` for the current `msg.sender` chain" is **false**. `onlyAllowedRecipient` in [1](#0-0)  only checks `isAllowedRecipient[msg.sender]`; it never checks that the `CircomData` argument is the one whose fields were bound into the proof's public inputs by the outer `Hinkal.transact` call.

Exploit path:
1. Attacker owns funds/proofs for their own genuine `Hinkal.transact()` call that routes to Emporium as external action (Emporium is a legitimately-allowed recipient of `Hinkal`, per [2](#0-1) ).
2. Inside `EmporiumUpgradeable.runAction`, `stack.ops` is decoded straight from attacker-controlled `circomData.externalActionData.externalActionMetadata` — none of the individual `op.endpoint`/`op.callData` values are proof-constrained. For a "Stateless Interaction" op, Emporium executes `op.endpoint.call{value: op.value}(op.callData)` with `msg.sender == Emporium` in that call frame, per [3](#0-2) .
3. If `Emporium` has been added to `isAllowedRecipient` of `DepositOnChainUtxosExternalAction` (via `setAllowedRecipients`, per [4](#0-3) ), the attacker sets `op.endpoint = DepositOnChainUtxosExternalAction` and `op.callData = abi.encodeCall(runAction, (forgedCircomData, [0,...]))`. This call passes `onlyAllowedRecipient` because `msg.sender == Emporium`.
4. `forgedCircomData` is entirely attacker-chosen bytes inside `op.callData` — it is never touched by `verifyProof`/`performHinkalChecks`. The attacker sets `forgedCircomData.originalSender = victim`, `erc20TokenAddresses = [victimToken]`, and `externalActionMetadata` decoding to `utxoAmounts` summing to any `tokenTotal` up to `type(uint256).max`.
5. `DepositOnChainUtxosExternalAction.runAction` computes `tokenTotal` from attacker data with no per-caller cap ( [5](#0-4) ) and calls `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)`, i.e. `IERC20(token).safeTransferFrom(victim, Emporium, tokenTotal)` ( [6](#0-5) ). This succeeds up to whatever allowance `victim` gave to `DepositOnChainUtxosExternalAction` (the msg.sender making the ERC20 call is `DepositOnChainUtxosExternalAction` regardless of who called `runAction`), i.e. up to `type(uint256).max` if the victim approved that.
6. Back in `EmporiumUpgradeable.runAction`, the stolen tokens now sitting on Emporium's balance are picked up by the `balancesAfter - balancesBefore` accounting ( [7](#0-6) ) and forwarded via `handleOut` to `msg.sender` of the *outer* call — which is `Hinkal.sol` itself ( [8](#0-7) ), returned as a `UTXO` for the attacker's stealth address.
7. `Hinkal.transact`'s balance-diff/UTXO-amount equality ( [9](#0-8) ) is self-consistent because the stolen funds and the outgoing UTXO amount match each other — the check only verifies internal bookkeeping, it never verifies that the funds legitimately originated from the attacker's own proof-verified deposit. The attacker ends the transaction with a freshly minted, fully backed (by stolen tokens) shielded UTXO.

Existing guards fail because: `onlyAllowedRecipient` binds only to `msg.sender`, not to the `CircomData` payload or its provenance; `performHinkalChecks`/`verifyProof` are only invoked once, on the *outer* `circomData` for the attacker's own legitimate transaction — the forged inner `CircomData` used in the nested call never passes through `Hinkal.transact` at all, so no root-hash, nullifier, or proof check ever sees it.

### Impact Explanation
Direct theft of a victim's ERC20 allowance, up to the full approved amount, and minting of shielded Hinkal UTXO value fully backed by the stolen tokens for the attacker — matching the Critical category ("direct theft of shielded or in-flight user funds, minting shielded value... without backing"). This is repeatable for every victim who has an outstanding approval to `DepositOnChainUtxosExternalAction` and costs the attacker only their own genuine, cheap `Hinkal.transact()` call plus gas.

### Likelihood Explanation
The finding is conditional on a specific configuration: `Emporium` (or any other allowed-recipient contract capable of making attacker-directed arbitrary calls, e.g. via `op.endpoint.call`) must be present in `DepositOnChainUtxosExternalAction`'s `isAllowedRecipient` mapping. That mapping is populated only by the constructor or by `onlyOwner`'s `setAllowedRecipients` — this repository's indexed contents contain no deployment script showing this cross-registration exists in production. If it does exist (or is added by the owner for any legitimate integration reason), the exploit requires no privileges from the attacker beyond a normal `Hinkal.transact()` call and a victim who previously approved `DepositOnChainUtxosExternalAction`. Given the uncertainty about whether this specific cross-allowlisting is or will be deployed, this should be treated as a design-level access-control gap rather than a currently-proven live exploit; it is nonetheless a Critical-severity architectural flaw because the whitelist offers no defense-in-depth against composition of two "trusted" action contracts.

### Recommendation
Bind `onlyAllowedRecipient` (and every external action's `runAction`) to the specific `CircomData` that was proof-verified by the outer `Hinkal.transact` call, e.g. by having `Hinkal.sol` pass a hash/commitment of the verified `circomData` alongside the call, and have each external action require `keccak256(abi.encode(circomData)) == expectedHash` set by `Hinkal` in the same call frame (or, simpler, disallow nested/cross external-action invocation entirely — require `tx.origin`/call-depth checks, or track a `reentrancyGuard`-style "active circomData" slot set only by `Hinkal.sol`). At minimum, never allow `DepositOnChainUtxosExternalAction` (or any action performing `transferFrom(originalSender, ...)`) to be reachable from a `msg.sender` that itself permits attacker-controlled arbitrary calls.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `EmporiumUpgradeable` (proxy), and `DepositOnChainUtxosExternalAction`; register both as external actions on `Hinkal`; set `DepositOnChainUtxosExternalAction.setAllowedRecipients([address(hinkal), address(emporium)])` to simulate the misconfiguration under test, and `Emporium`'s `allowedRecipients` to `[address(hinkal)]`.
2. Deploy a mock ERC20, mint to `victim`, have `victim` call `token.approve(address(depositAction), type(uint256).max)`.
3. Attacker generates a valid proof for their own trivial `Hinkal.transact()` call routed to `Emporium`, with `externalActionMetadata` decoding to an `EmporiumStack` containing one stateless `EmporiumOperation`: `endpoint = address(depositAction)`, `callData = abi.encodeCall(IExternalActionV2.runAction, (forgedCircomData, zeroDeltas))`, where `forgedCircomData.originalSender = victim`, `erc20TokenAddresses = [address(token)]`, `externalActionMetadata = abi.encode([[type(uint256).max])`.
4. Assert before: `token.balanceOf(victim) == V`, `token.allowance(victim, address(depositAction)) == type(uint256).max`.
5. Execute `hinkal.transact(...)` from attacker.
6. Assert after: `token.balanceOf(victim) == 0` (fully drained) and attacker's new shielded UTXO commitment for `token` with `amount == V` exists in the Merkle tree — proving the equality "victim's pre-tx allowance == amount stolen and re-minted as attacker's shielded value" and demonstrating the broken invariant that `runAction` callers cannot bound `tokenTotal` to the proof-verified transaction.

### Citations

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

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L30-37)
```text
    function setAllowedRecipients(
        address[] calldata recipients
    ) external onlyOwner {
        for (uint i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "zero address!");
            isAllowedRecipient[recipients[i]] = true;
        }
    }
```

**File:** contracts/Hinkal.sol (L97-146)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
```text
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

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L55-82)
```text
            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```

**File:** contracts/Transferer.sol (L74-81)
```text
    function transferERC20TokenFrom(
        address _erc20TokenAddress,
        address _from,
        address _to,
        uint256 _value
    ) internal {
        IERC20(_erc20TokenAddress).safeTransferFrom(_from, _to, _value);
    }
```
