### Title
ExternalActionSwap trusts raw output-token balance diff with no cap on input consumption, letting a crafted router call convert stranded/residual input-token balance into unbacked output — (File: contracts/external-actions/swaps/ExternalActionSwap.sol, contracts/external-actions/swaps/LifiExternalAction.sol)

### Summary
`ExternalActionSwap.swap()` computes `swappedAmount` purely from the output-token balance delta returned by `callRouter`, and never verifies that the router actually consumed only `inputAmount` of `inputToken`. Because `approveUnlimited` grants the router persistent max approval on `inputToken`, and no code sweeps or checks leftover `inputToken` balance, any pre-existing (residual) balance of that token sitting on the `ExternalActionSwap` contract can be pulled by attacker-crafted `externalActionMetadata` in a later `transact` and folded into that call's `swappedAmount`, producing an output UTXO larger than what the attacker's own debited `deltaAmounts[0]` legitimately backs.

### Finding Description
The equality that should hold per call is: *tokens leaving the action to the router == `inputAmount` = `uint256(-deltaAmounts[0])` that Hinkal actually debited from the caller's shielded balance/on-chain balance for that transaction* — i.e. `swappedAmount` should be attributable only to the specific `inputAmount` moved in this call.

Code path:
- `Hinkal._externalTransact` (contracts/Hinkal.sol:234-261) transfers exactly `uint256(-deltaAmountChanges[0])` of `inputToken` from Hinkal to the `ExternalActionSwap` contract, then calls `runAction`. [1](#0-0) 
- `ExternalActionSwap.swap` (contracts/external-actions/swaps/ExternalActionSwap.sol:40-68) sets `inputAmount = uint256(-deltaAmounts[0])` and passes it to `callRouter`, but `inputAmount` is never enforced as an upper bound on what the router actually pulls. [2](#0-1) 
- `LifiExternalAction.callRouter` (contracts/external-actions/swaps/LifiExternalAction.sol:16-36) grants unlimited, persistent approval to `router` on `inputToken` via `approveUnlimited`, then executes attacker-supplied `externalActionMetadata` calldata against the fixed router address, and derives `swappedAmount` solely from the *output*-token balance diff. There is no check anywhere on the `inputToken` balance before/after the call. [3](#0-2) [4](#0-3) 

Because `externalActionMetadata` is fully attacker-controlled (it's part of `CircomData` the prover builds), and the router already holds `type(uint256).max` approval on `inputToken` from any prior swap of that token by any user, an attacker can encode a swap instruction whose declared "amount in" exceeds the officially-debited `inputAmount` — pulling in any residual `inputToken` balance sitting on the `ExternalActionSwap` contract (left over from a partial fill, dust, or any other source) in addition to the legitimately-debited amount. The router happily converts the larger input into output token; `swappedAmount = balanceAfter - balanceBefore` on the output token faithfully reports the inflated amount, and `swap()` mints an on-chain UTXO (`utxoSet[0].amount = amountToSendToHinkal`) sized to that inflated amount.

Back in `Hinkal.transact`, the balance equation only checks Hinkal's own balance delta against `amountChanges[i] + utxoAmount` — and since the UTXO is constructed dynamically from the actual (inflated) balance change rather than from any circuit-fixed expected amount, the equality is tautologically satisfied. [5](#0-4) 

So the on-chain check that is supposed to prevent value creation never actually constrains the router's consumption of `inputToken`; it only reconciles Hinkal's own balance against the (already-inflated) UTXO amount produced by the swap. The genuine broken invariant is: *tokens consumed by the router from `ExternalActionSwap`'s balance can exceed `inputAmount` derived from `deltaAmounts[0]`, with no code anywhere checking `inputToken` balance before vs after the router call.*

### Impact Explanation
Any residual `inputToken` balance stranded on the shared `ExternalActionSwap` contract (from a prior partial fill by any user, dust, or leftover fee remainders) becomes a common pool that a subsequent unrelated caller can convert into a legitimately-credited shielded UTXO for themselves, without that amount ever being debited from their own `deltaAmounts`/`amountChanges`. This is a direct theft of other users' stranded funds and/or unbacked minting of shielded value, matching the Critical severity category (minting shielded value without backing / direct theft of in-flight funds). It is repeatable any time residue exists and the same token has previously been swapped through this action (establishing the unlimited router approval).

### Likelihood Explanation
Preconditions: (1) some `inputToken` balance must be sitting on the `ExternalActionSwap` contract beyond what the current call's `deltaAmounts[0]` accounts for — this can arise from partial fills, but is not strictly required to prove the underlying flaw, since the contract-level check that should bound router consumption to `inputAmount` simply does not exist; (2) the router must have previously been given (or must be given in the same call) unlimited approval on that token, which happens automatically via `approveUnlimited` on first use. The attacker's cost is only their own real swap transaction fees and control over `externalActionMetadata`, which they already fully control as an unprivileged depositor/prover. No privileged role is needed.

### Recommendation
In `ExternalActionSwap.callRouter` (and any implementation such as `LifiExternalAction`), measure and enforce the `inputToken` balance change as well: capture `inputToken` balance before/after the router call and require that the decrease equals exactly `inputAmount` (reverting otherwise), or refund/sweep any leftover input balance back to the Hinkal contract/depositor at the end of every `swap()` call so no residue can ever accumulate on `ExternalActionSwap`. Additionally, avoid granting `type(uint256).max` approval that persists indefinitely across unrelated calls/users — approve only the exact `inputAmount` needed for the specific call (reset to zero afterward), so the router can never pull more than what was legitimately debited in that transaction.

### Proof of Concept
Hardhat test plan:
1. Deploy `Hinkal`, `HinkalHelper`, and `LifiExternalAction` (or a mock `ExternalActionSwap` subclass) with a mock router.
2. Mock router's swap function: when called, pulls an attacker-specified `amountIn` of `inputToken` via `transferFrom` (using the unlimited approval) — not limited to the officially reported `inputAmount` — and sends back a proportional amount of `outputToken`.
3. Step A: directly transfer (or arrange via any means) a "residual" balance of `inputToken` onto the `ExternalActionSwap` contract address (simulating leftover from a prior partial fill), without any accompanying debit in Hinkal's ledger.
4. Step B: perform a legitimate small deposit/swap `transact` call where `deltaAmounts[0] = -X` (small real amount) is debited from the caller, but craft `externalActionMetadata` so the mock router pulls `X + residual` from `ExternalActionSwap` (using the pre-existing unlimited approval) and returns output proportional to `X + residual`.
5. Assert: `swappedAmount` (and the resulting UTXO amount credited to the attacker) exceeds what `X` alone would produce, proving `swappedAmount != -deltaAmounts[0]`-derived value — i.e., `ExternalActionSwap`'s own token balance (`getERC20OrETHBalance(inputToken)` before Step B vs after) decreased by more than `X`, violating "tokens leaving the action == -deltaAmountChanges it received," while Hinkal's own balance-equation check in `transact` still passes.
6. Assert VALUE_CONSERVATION fails: total `inputToken` consumed by the router across the two calls exceeds the sum of `deltaAmounts[0]` debited in Hinkal across those same calls.

### Citations

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

**File:** contracts/Hinkal.sol (L244-261)
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

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
    }
```

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
