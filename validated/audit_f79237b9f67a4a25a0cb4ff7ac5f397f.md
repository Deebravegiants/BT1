### Title
Unbounded router calldata in `LifiExternalAction.callRouter` lets any caller sweep stranded/residual `inputToken` balance into their own output UTXO - ([File: contracts/external-actions/swaps/LifiExternalAction.sol])

### Summary
`ExternalActionSwap.swap` computes `inputAmount = -deltaAmounts[0]` and passes it to `callRouter`, but `LifiExternalAction.callRouter`'s ERC20 branch never uses that parameter to bound what the router actually pulls. It only grants unlimited approval to the router and executes fully attacker‑controlled `externalActionMetadata` against it, then measures `swappedAmount` purely as the output‑token balance delta. Any pre‑existing/stranded `inputToken` balance sitting in the action contract (e.g. left over from a prior LI.FI partial‑fill refund, or dust from a fee‑on‑transfer‑token shortfall) can therefore be consumed by a subsequent attacker's swap call data, producing extra `swappedAmount` that is fully packaged into the attacker's own on‑chain UTXO.

### Finding Description
The invariant under test is: *tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx.* This is violated at the input-token side. [1](#0-0) 

`swap()` computes `inputAmount` from the declared `deltaAmounts[0]` and forwards it to `callRouter`, but the concrete implementation ignores it: [2](#0-1) 

For the ERC‑20 branch, `inputAmount` is dead code — the function only calls `approveUnlimited(inputToken, router)` and then executes `router.call(externalActionMetadata)`, where `externalActionMetadata` is entirely attacker-controlled (per the problem's attacker‑control list). The router therefore pulls whatever amount the attacker‑crafted calldata specifies via `transferFrom`, limited only by the unlimited allowance and the contract's actual token balance — not by the declared `inputAmount`/`deltaAmountChanges[0]` that Hinkal actually sent this transaction.

`swappedAmount` is measured only as the outputToken balance delta:
```
swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
```
This correctly excludes any pre‑existing *output*-token balance (since `balanceBefore` already contains it), but does nothing to exclude a pre-existing/stray *input*-token balance from being consumed by the router call. If such a stray balance exists (e.g. left behind by a previous LI.FI partial‑fill refund of unspent input tokens, which `LifiExternalAction` never sweeps back to Hinkal since only `outputToken` is transferred out at the end of `swap`, or dust produced when the input token is fee‑on‑transfer and the actually-delivered amount differs from the stated amount), a subsequent attacker can craft `externalActionMetadata` whose embedded `amountIn` covers `their own transferred inputAmount + the stray residual`. The router converts the full amount, inflating `swappedAmount`, and the entire result is packaged into the attacker's own UTXO: [3](#0-2) 

This UTXO amount then propagates back through `Hinkal.sol`'s only conservation check, which is purely self‑consistent (it ties actual on-chain balance movement to `amountChanges[i] + utxoAmount`, not to any circuit-verified cap on output size relative to input): [4](#0-3) 

Since the extra output genuinely arrived in Hinkal's balance (it really was swapped), this check passes even though the swap consumed more `inputToken` than Hinkal sent this transaction. `circomData.slippageValues[1]` is only a *minimum* floor on output — there is no maximum/ceiling check anywhere (contract or circuit) tying output size to the actual `-deltaAmountChanges[0]` transferred this call. The circuit's `inTotal + amountChanges[i] === outTotal` constraint only governs the shielded UTXO commitment math for the prover's own declared amounts; it has no knowledge of the actual router execution or the action contract's real token balances.

### Impact Explanation
An attacker can capture stranded/residual `inputToken` balance belonging to the protocol/other users' in-flight funds and convert it into their own shielded output UTXO, i.e. direct theft of in-flight/protocol funds parked in the external action contract. This matches the Critical impact category ("direct theft of shielded or in-flight user funds"). It is repeatable any time residual balance accumulates in the action (e.g., from LI.FI partial-fill refunds or fee-on-transfer-token delivery shortfalls in prior transactions), and the attacker only needs to observe the action contract's `inputToken` balance and craft matching router calldata.

### Likelihood Explanation
Requires (1) some `inputToken` balance to be sitting in the `LifiExternalAction` contract beyond what the current transaction supplies (achievable via a prior LI.FI refund, or by using a fee-on-transfer token to create shortfalls/dust across transactions), and (2) the attacker's ability to fully control `externalActionMetadata` for the LI.FI router call, which the threat model grants. No privileged role is needed; cost is limited to gas and constructing valid LI.FI calldata. This is realistically triggerable by any user monitoring the action contract's token balances.

### Recommendation
In `LifiExternalAction.callRouter`, track and enforce the actual `inputToken` balance consumed by the router call against the passed-in `inputAmount` (e.g., measure `inputToken` balance before/after the router call and require `balanceBefore - balanceAfter <= inputAmount`), and sweep/refund any leftover input token back to Hinkal/the depositor rather than leaving it stranded in the action contract. Avoid unlimited/standing approvals that let arbitrary future calldata pull more than intended, and never let stray balances be silently available to be scooped up by unrelated transactions.

### Proof of Concept
Foundry plan:
1. Deploy `Hinkal`, `LifiExternalAction` (with a mock router mimicking LI.FI's `call`-based interface), a fee-on-transfer or plain ERC20 `inputToken`, and an `outputToken`.
2. Seed the residual: perform a first `transact` swap where the mock router, upon receiving the swap call, refunds/leaves a stray `inputToken` balance in `LifiExternalAction` (simulate a partial-fill refund, or use a fee-on-transfer `inputToken` so the router receives less than the declared `amountIn` and the contract retains the unspent remainder).
3. Assert `IERC20(inputToken).balanceOf(lifiAction) > 0` after tx 1 (residual established).
4. As an unrelated attacker, submit tx 2: deposit/prove a small `deltaAmountChanges[0]` for `inputToken`, but craft `externalActionMetadata` so the mock router's calldata specifies `amountIn = declaredInputAmount + residualBalance`.
5. Assert the mock router successfully pulls `declaredInputAmount + residualBalance` (not just `declaredInputAmount`) via `transferFrom`, confirming `inputAmount` parameter is unenforced.
6. Assert the resulting output UTXO amount (`amountToSendToHinkal`) exceeds what a swap of only `declaredInputAmount` would have produced, i.e. `swappedAmount` includes value derived from the stray residual, and that this excess ends up addressed to the attacker's own `stealthAddressStructure`, thereby violating `tokens leaving the action == -deltaAmountChanges Hinkal sent it` for the input leg of that transaction.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-68)
```text
    function swap(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) internal returns (UTXO[] memory utxoSet) {
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }

        address outputToken = circomData.erc20TokenAddresses[1];

        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );

        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L89-102)
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
    }
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

**File:** contracts/Hinkal.sol (L134-146)
```text
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
