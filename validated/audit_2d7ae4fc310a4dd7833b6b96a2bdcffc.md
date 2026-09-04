### Title
Residual/dust ERC-20 balance in `LifiExternalAction`/`ExternalActionSwap` can be swept by any subsequent swap caller via unbounded `approveUnlimited` router allowance - ([File: contracts/external-actions/swaps/LifiExternalAction.sol], [File: contracts/external-actions/swaps/ExternalActionSwap.sol])

### Summary
`ExternalActionSwap.swap` computes the amount credited to the caller's own output UTXO purely from the action contract's own before/after token balance (`swappedAmount`), while the actual amount pulled from that balance by the LI.FI router is dictated entirely by attacker-controlled `externalActionMetadata`, not by the `inputAmount` (`-deltaAmounts[0]`) Hinkal actually sent for that transaction. Because `LifiExternalAction.callRouter` grants the router a persistent, effectively unlimited `approve` via `approveUnlimited` and never checks that only `inputAmount` of `inputToken` was consumed, any residual/stranded `inputToken` balance already sitting in the shared action contract (from a prior, unrelated transaction) can be swept into the current swap and credited to the attacker's own UTXO, in addition to their own legitimate trade.

### Finding Description
The invariant that should hold is: value leaving the action contract in a transaction (`swappedAmount`, hence the attacker's UTXO amount) should equal only what Hinkal parked there for that transaction, i.e. `uint256(-deltaAmounts[0])`. Instead, the code enforces no such bound.

- `ExternalActionSwap.swap` computes `inputAmount = uint256(-deltaAmounts[0])` and passes it to `callRouter`, but for the ERC20 path in `LifiExternalAction.callRouter`, `inputAmount` is never used to bound anything: [1](#0-0) [2](#0-1) 

- `approveUnlimited` sets (or leaves) an allowance of `type(uint256).max` for the `router` on `inputToken` and is not reset per-transaction: [3](#0-2) 

- `swappedAmount` is derived only from the *output* token's before/after balance on the action contract (`getERC20OrETHBalance(outputToken)`), not from verifying that exactly `inputAmount` of `inputToken` was debited. The attacker fully controls `externalActionMetadata` (the raw calldata forwarded to `router.call(...)`), so they can craft LI.FI calldata that pulls the entire `inputToken` balance of the action contract - `inputAmount` plus any leftover dust from a prior transaction - and route the resulting larger output to themselves.

- Hinkal's own accounting check does not catch this because it only compares the *Hinkal contract's* own balance delta against `amountChanges`/`utxoAmount` for the transaction, not the action contract's internal balance usage: [4](#0-3) 
For the swap's output token, `balanceDif` (Hinkal's balance increase) is caused by the very same transfer that produces `utxoAmount`, so the check `balanceDif == amountChanges[i] + utxoAmount` is tautological for external-action outputs and enforces nothing about the *size* of `utxoAmount` relative to what was actually contributed on the input side. On the input side, Hinkal only verifies it sent exactly `inputAmount` to the action - it has no visibility into whether the action then spent more than that internally.

- `_externalTransact` in `Hinkal.sol` only forwards `-deltaAmountChanges[i]` to the action address; it has no mechanism to verify the action's post-call balance for `inputToken` returns to zero or matches exactly what was sent: [5](#0-4) 

**Exploit flow:**
1. Some prior transaction (a legitimate user's swap, a partial-fill/positive-slippage LI.FI route, or any transfer) leaves `inputToken` dust sitting in the `LifiExternalAction` contract's own balance (this contract is shared across all users, not per-user).
2. Attacker submits their own `Hinkal.transact` call with `externalActionData.externalActionId` pointing at the swap action, `erc20TokenAddresses = [inputToken, outputToken]`, and a small legitimate `deltaAmounts[0]` (their own deposit).
3. Attacker crafts `externalActionMetadata` (the raw LI.FI router calldata) to swap the *entire* current `inputToken` balance of the action contract (their own contribution + the pre-existing dust), relying on the already-unlimited router approval set by `approveUnlimited` in a prior call.
4. `callRouter` measures only `outputToken` before/after and returns the inflated `swappedAmount`; `swap()` sends the whole inflated amount (minus fees) to the attacker's own `stealthAddressStructure` as their output UTXO.
5. Hinkal-level checks pass because they only verify Hinkal's own balance delta for `inputToken` (exactly `-inputAmount`, matching what the attacker declared) and the tautological output-token equation - neither constrains the action's internal over-consumption of dust.

The attacker walks away with more output value than their own input warrants, funded entirely by stranded/residual funds that belonged to the protocol/other users' in-flight transactions.

### Impact Explanation
Direct theft of in-flight/stranded protocol funds parked temporarily in the shared `LifiExternalAction`/`ExternalActionSwap` contract, captured as unearned value in the attacker's own shielded output UTXO. This is repeatable any time residual balance accumulates in the action contract (e.g., after any swap that under-consumes its transferred input due to partial fills, refunds, or rounding). Matches Critical: "direct theft of shielded or in-flight user funds."

### Likelihood Explanation
Requires: (1) a nonzero residual `inputToken` balance in the action contract from a prior transaction (plausible given LI.FI multi-hop/partial-fill routes and no per-tx sweep-to-zero enforcement), and (2) the attacker's ability to freely craft `externalActionMetadata` for their own transaction, which is explicitly permitted by the protocol design (attacker chooses proof/calldata for their own transact call). No privileged role is needed; cost is just gas plus their own genuine trade amount. Detection of available dust requires only reading the action contract's public token balance on-chain, which is trivial and repeatable.

### Recommendation
In `LifiExternalAction.callRouter` (and any other `ExternalActionSwap` subclass), measure and bound the `inputToken` balance consumed by the router call to exactly `inputAmount`: record `inputToken` balance before/after the router call and require the decrease equals `inputAmount` (reverting otherwise), or use a bounded, per-call `approveERC20Token(inputToken, router, inputAmount)` reset to zero after the call instead of `approveUnlimited`, so the router can never pull more than the amount intended for that transaction. Additionally, sweep/refund any unused input dust back to Hinkal (or disallow it from remaining in the action contract) so stray balances cannot accumulate as an exploitable target.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `LifiExternalAction` (mock LI.FI router), register the action.
2. Simulate a "prior transaction" leaving residual `inputToken` balance in the `LifiExternalAction` contract (e.g., directly transfer dust tokens to it, or execute one legitimate swap where the mock router only partially consumes the approved amount, leaving leftover balance and the unlimited approval set by `approveUnlimited`).
3. As attacker, call `Hinkal.transact` with a valid proof for a small genuine `deltaAmounts[0] = -X` (their own input), but craft `externalActionMetadata` so the mock router's `transferFrom` pulls `X + dust` instead of `X`.
4. Assert: `swappedAmount` / attacker's resulting UTXO amount > proportional amount expected from `X` alone, i.e., tokens leaving the action in this tx (`X + dust`) != `-deltaAmountChanges` Hinkal sent it (`X`) — breaking the target equality.
5. Assert the `LifiExternalAction` contract's `inputToken` balance dropped by `X + dust` instead of `X`, while Hinkal's own balance/slippage checks (`Hinkal.sol` lines 97-146) still pass, proving existing guards do not catch the divergence.

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

**File:** contracts/Hinkal.sol (L232-261)
```text
    ///@notice internal function to use Hinkal with external contracts.
    ///@param circomData circom data.
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
