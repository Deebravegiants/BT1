Confirmed: `approveUnlimited` sets `type(uint256).max` allowance to the router and persists across transactions since it's stored on-chain per token/spender pair.

### Title
LiFi swap fee stranding + persistent unlimited router approval lets an attacker drain accumulated residual tokens into their own credited UTXO - (File: contracts/external-actions/swaps/ExternalActionSwap.sol, contracts/external-actions/swaps/LifiExternalAction.sol)

### Summary
When `circomData.relay == address(0)` (a legitimate self-submit path allowed by `HinkalHelper.performHinkalChecks` when `originalSender == sender`), `sendToRelay` is a no-op, so `relayFee`/`hinkalFee` amounts computed in `ExternalActionSwap.swap` are deducted from `amountToSendToHinkal` but never leave the `LifiExternalAction` contract, permanently stranding fee tokens there. Because `LifiExternalAction.callRouter` grants the LI.FI `router` an unlimited, persistent ERC20 approval via `approveUnlimited` and never checks how much input-token balance the router actually consumed, an attacker can, in a later self-crafted swap for the same input token, supply router calldata that pulls the stranded residual (plus their own deposit) from the action contract and swap it, so `swappedAmount = balanceAfter - balanceBefore` on the output token is inflated by value the current transaction's `deltaAmountChanges` never accounted for. That larger `swappedAmount` becomes `amountToSendToHinkal`, which Hinkal accepts as a valid UTXO because its own balance check only compares Hinkal's own balance delta on the output token to what the action forwarded.

### Finding Description
The broken equality is: value credited into the new UTXO (`amountToSendToHinkal`, ultimately `utxoAmount` checked in `Hinkal.sol`'s balance equation) should equal the value this specific transaction's `deltaAmountChanges[0]` moved into the action, net of fees. Instead it equals `swappedAmount - totalFee`, where `swappedAmount` is derived purely from the action contract's own output-token balance delta with no constraint tying it to the amount of input token actually deposited by Hinkal for this call.

Root cause, step by step:
1. In `ExternalActionSwap.swap` (contracts/external-actions/swaps/ExternalActionSwap.sol:70-91), when `feeStructure.feeToken == inputToken != outputToken`, `inputAmount` used for the swap is reduced by `flatFee`, leaving `flatFee` worth of `inputToken` un-swapped in the contract. That residue is later routed via `sendToRelay(circomData.relay, relayFee, feeStructure.feeToken)`.
2. `sendToRelay` (contracts/Transferer.sol:178-190) is a no-op whenever `relay == address(0)`: `if (relay != address(0) && actualAmount > 0)`.
3. `relay == address(0)` is a legitimate, attacker-reachable state per `HinkalHelper.performHinkalChecks` (contracts/HinkalHelper.sol:213-219), which permits it whenever `circomData.originalSender == sender`.
4. Consequently the `flatFee` residue of `inputToken` is stranded permanently inside the `LifiExternalAction` contract's own balance.
5. `LifiExternalAction.callRouter` (contracts/external-actions/swaps/LifiExternalAction.sol:16-36) calls `approveUnlimited(inputToken, router)` (contracts/TransfererBase.sol:32-43), which sets a `type(uint256).max` allowance that persists across transactions, and then executes fully attacker-controlled `externalActionMetadata` against `router` with no post-call check on how much `inputToken` balance was actually consumed - only `outputToken` balance delta (`swappedAmount`) is measured.
6. In a subsequent transaction using the same `inputToken`, the attacker (who already caused/observed the stranded residue) crafts `externalActionMetadata` instructing the router to pull an amount of `inputToken` from the action contract larger than what Hinkal transferred for that transaction (up to the residue plus the attacker's own new deposit), consuming the previously stranded balance under the pre-existing unlimited approval.
7. The resulting `swappedAmount` (and hence `amountToSendToHinkal`) is inflated by value not sourced from this transaction's `deltaAmountChanges[0]`. Hinkal's balance-equation check in `Hinkal.sol` (lines 88-146) only verifies that Hinkal's own token balance moved consistently with `amountChanges`/`utxoAmount` - it has no visibility into, or check on, the action contract's internal token accounting - so the inflated UTXO passes all checks and is credited to the attacker.

Existing guards do not prevent this: `performHinkalChecks` validates `relay`/`originalSender` consistency but does not forbid `relay == address(0)`; the Hinkal balance equation (contracts/Hinkal.sol:134-146) is self-consistent only from Hinkal's own before/after balances, and cannot detect that the action's `swappedAmount` was inflated using its own stranded prior-transaction balance; `checkOnchainCreation` and the circuit's `inTotal + amountChanges === outTotal` are only invariants over amounts declared in `circomData`, which the attacker still supplies consistently with the (inflated) UTXO they mint off-chain.

### Impact Explanation
This lets an attacker mint a shielded UTXO larger than the value actually delivered to the `LifiExternalAction`/Hinkal system in that transaction, by recycling stranded relay/protocol fee funds (or any other dust/residual left in the action contract) that never belonged to that transaction. Repeated over time as residues accumulate (each `relay == address(0)` swap can strand more fee tokens), this is a repeatable mechanism for extracting value beyond what a given transaction's proof-authorized `amountChanges` justify - matching "High: theft ... of protocol/relay fees" at minimum, and depending on volume of stranded balance, could approach direct theft of value that should have flowed to relays/protocol.

### Likelihood Explanation
Preconditions: at least one prior transaction (which the attacker themselves can trigger, since `relay == address(0)` requires only `originalSender == sender`, both attacker-controlled) must leave a residue of a given `inputToken` in the `LifiExternalAction` contract. The attacker then needs the router's calldata semantics to allow specifying a `transferFrom` amount larger than the amount actually deposited for that call, drawing on the already-approved unlimited allowance. This is fully within an unprivileged EOA's capability (craft `externalActionMetadata`, choose `feeStructure`, `timeStamp`, `relay=address(0)`) and costs only gas plus the fee they'd strand in the seeding transaction. It is repeatable and compounds as more residue accumulates.

### Recommendation
- Do not silently no-op fee payment when `relay == address(0)`; either forbid non-zero `relayFee`/`hinkalFee` in that path, revert if the fee cannot be paid, or route it to a fixed protocol treasury address instead of stranding it in the action contract.
- In `LifiExternalAction.callRouter`, measure and bound the actual `inputToken` balance consumed by the router call (e.g., require `balanceBefore(inputToken) - balanceAfter(inputToken) <= inputAmount`), rather than trusting `outputToken` delta alone.
- Avoid persistent unlimited approvals to the router across independent transactions, or reset/limit the approval to exactly `inputAmount` per call.

### Proof of Concept
Foundry test plan:
1. Deploy `LifiExternalAction` with a mock router that implements a generic `swap(address from, address to, uint256 fromAmount, uint256 toAmount)`-style call performing `transferFrom(action, mockRouter, fromAmount)` then `transfer(action, toAmount)` in a different output token (fully attacker-specified `fromAmount`/`toAmount`).
2. Tx A: attacker calls Hinkal.transact with the LiFi action, `relay = address(0)`, `originalSender = attacker`, `inputToken = feeStructure.feeToken`, `outputToken != inputToken`, nonzero `flatFee`. Assert after the call that `IERC20(inputToken).balanceOf(action) == flatFee` (stranded residue) and `router` allowance for `inputToken` is `type(uint256).max`.
3. Tx B: attacker calls Hinkal.transact again with the same `inputToken`, depositing a small `deltaAmount`, but crafts `externalActionMetadata` so the mock router pulls `deltaAmount + flatFee` (i.e., includes the stranded residue) and returns a proportionally larger `toAmount` of `outputToken`.
4. Assert: `amountToSendToHinkal` (and the UTXO amount credited by Hinkal) in Tx B exceeds `(inputAmount from Tx B's deltaAmountChanges) - totalFee` scaled by the router's true exchange rate - i.e., `utxoAmount_B > f(deltaAmountChanges_B[0])`, proving the credited UTXO includes value never deposited by Hinkal in that transaction, while `IERC20(inputToken).balanceOf(action)` after Tx B drops to 0 (the stranded residue has been fully drained into attacker's UTXO). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/Transferer.sol (L178-190)
```text
    function sendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) internal {
        if (relay != address(0) && actualAmount > 0) {
            transferERC20TokenOrETH(
                erc20TokenAddress,
                relay,
                uint256(actualAmount)
            );
        }
    }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-97)
```text
        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );

        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );

        if (circomData.feeStructure.feeToken == outputToken) {
            sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
        } else {
            sendToRelay(
                circomData.relay,
                relayFee,
                circomData.feeStructure.feeToken
            );
            sendToRelay(circomData.relay, hinkalFee, outputToken);
        }

        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);

        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
```

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L16-36)
```text
    function callRouter(
        address inputToken,
        uint256 inputAmount,
        address outputToken,
        bytes calldata externalActionMetadata
    ) internal override returns (uint256 swappedAmount) {
        uint256 balanceBefore = getERC20OrETHBalance(outputToken);

        if (inputToken == address(0)) {
            (bool success, ) = router.call{value: inputAmount}(
                externalActionMetadata
            );
            require(success, "LI.FI swap failed: native coin");
        } else {
            approveUnlimited(inputToken, router);
            (bool success, ) = router.call(externalActionMetadata);
            require(success, "LI.FI swap failed: erc-20 token");
        }

        swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
    }
```

**File:** contracts/TransfererBase.sol (L32-43)
```text
    function approveUnlimited(
        address _erc20TokenAddress,
        address _to
    ) internal {
        if (
            IERC20(_erc20TokenAddress).allowance(address(this), _to) <
            type(uint256).max / 2
        ) {
            IERC20(_erc20TokenAddress).safeApprove(_to, 0);
            IERC20(_erc20TokenAddress).safeApprove(_to, type(uint256).max);
        }
    }
```

**File:** contracts/HinkalHelper.sol (L213-219)
```text
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );
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
