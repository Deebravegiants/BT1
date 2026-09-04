### Title
Unauthorized third-party can drain Emporium's shared order/position proceeds via unsigned `EmporiumOperation`s - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` credits the caller's own Hinkal UTXO with `balancesAfter - balancesBefore` computed *within the same call*, and lets any Hinkal user supply arbitrary `stack.ops` with `signerAddress == address(0)` (the "stateless" path) without any signature or ownership check. Because Emporium is a single, shared on-chain identity for every user's resting order/position placed this way, an unrelated attacker can submit their own valid Hinkal proof whose `externalActionMetadata` calls the external order book's "claim/collect" function for a victim's already-settled position, capturing the entire proceeds into their own shielded output.

### Finding Description
The claimed equality is: *the account that receives the settled proceeds credited via `runAction` == the account whose order/proof produced the settlement (the victim)*. In practice it is *whoever supplies the matching `stack.ops` in a `runAction` call*, with no binding between the `EmporiumOperation`s executed and the `circomData`/proof owner.

In `runAction` [1](#0-0) , `stack.ops` is decoded straight from `circomData.externalActionData.externalActionMetadata` — fully attacker-controlled data inside their own proof — and dispatched via `verifyWallet`. When `stack.signerAddress == address(0)` ("CASE 2: Stateless Interaction"), `verifyWallet` only checks/marks `usedMessages[emporiumMessage]`; it performs **no signature check at all** and returns immediately [2](#0-1) . The only restriction on the raw call is that the selector isn't `callHinkalWallet`/`doSendToRelay` [3](#0-2) ; any other `op.endpoint.call(op.callData)` executes with Emporium itself as `msg.sender`.

Because a victim's limit order/position placed through this stateless path is owned on-chain by the Emporium contract's address (a single shared identity across all users of this mechanism, not per-user), any external protocol permission check based on `msg.sender == position owner` is satisfied for **any caller** who routes through Emporium — including an unrelated attacker. The credited amount is computed purely from the balance delta observed during that specific call:
```
int256 balanceChange = int256(balancesAfter[i]) - int256(balancesBefore[i]);
if (deltaAmountChanges[i] < 0) { balanceChange -= deltaAmountChanges[i]; }
```
and is paid straight to `msg.sender` (Hinkal) and shielded to `circomData.stealthAddressStructure` — the attacker's own address — via `handleOut` [4](#0-3) . `runAction` is only reachable from `Hinkal._externalTransact`, gated by `onlyAllowedRecipient`, but that only restricts the caller to be the Hinkal contract, not to be the victim — any Hinkal user submitting their own valid ZK proof/`CircomData` reaches this code path with attacker-chosen `externalActionMetadata` [5](#0-4) .

None of the existing guards prevent this: `performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `rootHashExists`, and the calldata-hash integrity check in `HinkalHelper` only validate the *internal consistency* of the attacker's own proof/`CircomData` (their own nullifiers, amounts, hash of their own calldata) — none of them constrain what the freely-chosen `externalActionMetadata` bytes actually do to external contracts, nor tie a specific order/position to the account whose proof authorized its creation. The slippage/balance-equality checks in `Hinkal.transact` [6](#0-5)  only ensure the attacker's own UTXO output matches the balance delta they engineered — they do not verify the source of that delta is the attacker's own prior deposit.

### Impact Explanation
Direct theft of shielded/in-flight user funds: any unprivileged attacker who deposits into Hinkal (arbitrary amount, even zero) and crafts their own proof can drain the proceeds of another user's resting order/position that is settled and sitting behind Emporium's shared identity, by including a claim/collect call to the relevant external protocol in their own `stack.ops`. This is repeatable for every victim order placed through the unsigned/stateless Emporium path and matches "Critical - direct theft of shielded ... user funds."

### Likelihood Explanation
Preconditions: a victim must have placed an order/position via Emporium's stateless (`signerAddress == address(0)`) path such that the external protocol's claim/collect function is permissionless once called by the position owner (Emporium). The attacker needs only their own Hinkal deposit/proof (arbitrary amount) and knowledge of the victim's order/position parameters (observable on-chain), no privileged role, no compromised keys. Attacker cost is a single Hinkal transaction; the race requires only broadcasting before the victim's own withdrawal, and can even be attempted opportunistically any time between settlement and the victim's claim, making it highly feasible and repeatable across multiple victims/orders.

### Recommendation
Bind `EmporiumOperation` execution and the resulting settlement credit to the account that owns the underlying order: require an authenticated signature (or an on-chain per-order owner mapping keyed by `emporiumMessage`/order id) even for the "stateless" path, and only allow the recorded owner (or their authorized relay) to trigger `runAction` calls that claim proceeds for that specific order/position. Alternatively, track settled-but-unclaimed balances per order/owner rather than crediting the entire ambient balance delta to whichever caller happens to invoke `runAction` next.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, and a mock external order-book/DEX contract whose `placeOrder`/`fill` credits the caller (Emporium) with proceeds, and whose `collect(orderId)` pays out to `msg.sender` (Emporium) — modeling a Uniswap-V3-range-order/GTC-book claim function callable by anyone once the caller is the recorded owner.
2. Victim: generate a valid proof/`CircomData` with `emporiumMessage = M1`, `stack.signerAddress = address(0)`, `stack.ops = [placeOrder(...)]`; call `Hinkal.transact` — order now owned by Emporium, unsettled.
3. Externally (no Hinkal involvement), fill the order against the mock book so proceeds accumulate on Emporium's token balance as "claimable" via `collect(orderId)`.
4. Attacker: independently deposit into Hinkal, generate their own valid proof/`CircomData` with `emporiumMessage = M2`, `stack.signerAddress = address(0)`, `stack.ops = [collect(orderId)]`, `stealthAddressStructure = attacker's own`; call `Hinkal.transact` before the victim's own withdrawal transaction.
5. Assert: attacker's resulting shielded UTXO amount equals the victim's settled proceeds (`balanceChange` computed in `runAction`), and a subsequent victim `runAction`/withdrawal call for the same order yields zero — proving `first successful caller of runAction == fund recipient`, independent of order authorship, and that this diverges from the victim being the rightful recipient.

### Citations

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
