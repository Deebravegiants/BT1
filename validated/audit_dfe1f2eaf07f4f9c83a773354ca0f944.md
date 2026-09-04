### Title
Standing `approveUnlimited` allowance + unchecked input consumption in `ExternalActionSwap.swap`/`LifiExternalAction.callRouter` lets an attacker drain stranded input-token balance into their own output UTXO - (File: contracts/external-actions/swaps/ExternalActionSwap.sol, contracts/external-actions/swaps/LifiExternalAction.sol)

### Summary
`ExternalActionSwap.swap` computes the amount to credit to the caller purely from the **output-token** balance delta around the router call (`callRouter`), and never verifies that the router actually consumed exactly `inputAmount` of the **input token** it was given for that transaction. Combined with `approveUnlimited` (contracts/TransfererBase.sol:32-43) leaving a standing `type(uint256).max` allowance from the action contract to the LI.FI router, any residual/stranded input-token balance sitting in the action contract (e.g. left over because a prior swap under-consumed its declared input) can be pulled by the router on a later, unrelated attacker's transaction and converted into extra output that is credited entirely to that attacker's UTXO.

### Finding Description
The invariant that should hold is: *tokens leaving the `ExternalActionSwap` action contract in a transaction == -deltaAmountChanges Hinkal sent it in that same transaction*.

Trace:
- `Hinkal._externalTransact` sends the action exactly `-deltaAmountChanges[i]` of the input token [1](#0-0) .
- `ExternalActionSwap.swap` reads `inputAmount = uint256(-deltaAmounts[0])` [2](#0-1)  and passes it to `callRouter`, but `callRouter`/`LifiExternalAction.callRouter` never checks that the router actually consumed exactly `inputAmount` of the input token - it only measures the **output**-token balance delta before/after the arbitrary `externalActionMetadata` call [3](#0-2) .
- `approveUnlimited` sets a persistent `type(uint256).max` allowance from the action contract to `router` once, and re-uses it across all future calls without ever reducing it back to what is needed for the current swap [4](#0-3) .
- Because `externalActionMetadata` is fully attacker-controlled raw calldata forwarded verbatim to `router.call(...)` [5](#0-4) , and there is no on-chain check tying the bytes to `inputAmount`, an attacker can construct metadata that instructs the router to pull more of the input token from the action contract than the `inputAmount` that was transferred to it for this specific transaction - as long as the router still has the standing max allowance and the action contract actually holds that extra balance (e.g. dust left behind by a prior transaction whose swap under-consumed its declared input, or ETH/tokens sent directly to the action's `receive()` [6](#0-5) ).
- `swappedAmount` (and hence `amountToSendToHinkal` and the attacker's `utxoSet[0].amount`) is entirely balance-delta based [7](#0-6) , so any surplus output produced by consuming stranded input is silently folded into the attacker's own shielded UTXO.
- `Hinkal.transact`'s top-level balance check [8](#0-7)  only verifies that Hinkal's own balance change equals `amountChanges[i] + utxoAmount`; it has no visibility into whether the tokens the action returned were legitimately backed by the exact `-deltaAmountChanges` sent to the action for that transaction. Because the extra tokens genuinely moved (action → Hinkal), this check passes even though the surplus was never debited from the attacker via `-deltaAmountChanges` this transaction.

None of `performHinkalChecks`, `verifyProof`, `rootHashExists`, or the slippage/balance requires constrain the router calldata's actual token consumption against the declared `inputAmount`; the circuit only constrains the shielded-side accounting (`inTotal + amountChanges === outTotal`), not what happens to funds once they leave Hinkal into the external action.

### Impact Explanation
An unprivileged attacker can extract input-token balance stranded in the `ExternalActionSwap`/`LifiExternalAction` contract (belonging to the protocol float or another user's in-flight/refunded funds) and have it swapped and credited as their own shielded output UTXO, beyond what `-deltaAmountChanges` authorized for their transaction. This is direct theft of in-flight/protocol funds routed through a Hinkal external action, matching Critical severity ("direct theft of shielded or in-flight user funds"). The technique is repeatable each time residual balance accumulates in the action contract, and since the LI.FI router and the `LifiExternalAction` deployment pattern are expected to be similarly configured on both Base and Arbitrum, the same crafted `externalActionMetadata` technique (not a literal proof/nullifier replay, since trees/nullifiers are chain-scoped) can be reused on both chains independently to repeat the theft wherever stranded balance exists.

### Likelihood Explanation
Preconditions: (1) the action contract must hold input-token balance beyond what any single in-flight transaction accounts for - achievable because `swap`/`callRouter` never enforce that a swap fully consumes its declared `inputAmount`, so an attacker can even self-seed the residue in a first transaction (under-consuming their own declared input) and reclaim/redirect it via calldata crafted for a following transaction; (2) `approveUnlimited` must have already been triggered for the token/router pair, which happens automatically on the first ERC-20 swap for that token. Both preconditions are trivially attacker-controllable at low cost (gas + one prior swap), making this a cheap, repeatable exploit rather than a rare edge case.

### Recommendation
In `ExternalActionSwap.swap` (or `callRouter`), snapshot the action contract's input-token balance immediately before the router call and require that the balance decrease by exactly `inputAmount` (no more, no less) after the call. Additionally, avoid persistent max approvals to the router; approve only `inputAmount` immediately before the call and reset the allowance to zero afterward, so a standing allowance can never be leveraged by an unrelated, later transaction to pull more than what was explicitly authorized for it.

### Proof of Concept
Foundry test plan:
1. Deploy `LifiExternalAction` with a mock router that supports `transferFrom`-based pulls of arbitrary declared amounts from calldata.
2. Transaction A (attacker, self): declare `inputAmount = X` via `deltaAmounts`, craft `externalActionMetadata` so the mock router only pulls `X - r` (leaving residue `r` of input token stranded in the action contract, e.g. via slippage-tolerant swap logic), assert the action contract's input-token balance increases by `r` after the tx (equality broken: tokens consumed by router != `-deltaAmountChanges` fully spent).
3. Transaction B (same or different attacker): declare a new legitimate `inputAmount = Y`, but craft `externalActionMetadata` for the mock router to pull `Y + r` (using the standing unlimited allowance from Transaction A plus the residual `r`), assert `swappedAmount`/`amountToSendToHinkal`/`utxoSet[0].amount` reflects the swap of `Y + r`, not `Y`.
4. Assert on both sides of the invariant: LHS = actual input-token balance decrease of the action contract during transaction B == `Y + r`; RHS = `-deltaAmountChanges[0]` Hinkal sent the action for transaction B == `Y`. LHS ≠ RHS confirms the violation, and the attacker's UTXO amount for transaction B is inflated by the value corresponding to `r`, which was never debited from them.

### Citations

**File:** contracts/Hinkal.sol (L96-146)
```text
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
```

**File:** contracts/Hinkal.sol (L244-256)
```text
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
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L31-31)
```text
    receive() external payable {}
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L44-49)
```text
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L89-101)
```text
        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);

        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
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
