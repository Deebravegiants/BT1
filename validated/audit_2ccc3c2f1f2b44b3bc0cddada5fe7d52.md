### Title
Emporium's arbitrary op-call execution lets any user drain ERC20 balances held by the shared Emporium contract that fall outside the equality checks - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` (the Emporium "external action" invoked from `Hinkal._externalTransact`) executes a caller-supplied list of `EmporiumOperation`s with essentially no restriction on the call target (`op.endpoint`) or calldata in the "stateless" branch. The only accounting safety net is a balance-equality check performed *per token listed in `circomData.erc20TokenAddresses`*, comparing the Emporium contract's own balance before/after the whole batch of ops. Any ERC20 balance sitting on the shared Emporium contract for a token that the attacker simply omits from `erc20TokenAddresses` is invisible to this check and can be swept to an arbitrary address by an unprivileged op, exactly mirroring the H01 root cause of "value moved but not counted in the balance equation."

### Finding Description
`Hinkal.transact()` only verifies that **Hinkal's own** balance delta for each token in `circomData.erc20TokenAddresses` matches `amountChanges[i] + utxoAmount`: [1](#0-0) 

It never inspects what happens inside the external action (Emporium) beyond this net effect on Hinkal's balance. Within `EmporiumUpgradeable.runAction`, the only internal equality check is likewise scoped strictly to `circomData.erc20TokenAddresses`: [2](#0-1) 

The stateless op branch performs a fully attacker-controlled low-level call from the Emporium contract's own context, with `op.endpoint` and `op.callData` supplied by the `EmporiumStack` decoded straight out of `circomData.externalActionData.externalActionMetadata`: [3](#0-2) 

The only signature verification (`verifyWallet`) is a no-op when `stack.signerAddress == address(0)`, meaning stateless ops require no signature check at all: [4](#0-3) 

Because Emporium is a single shared contract (not a per-user vault), any ERC20 tokens that end up resting on its balance — leftover dust from prior swaps/ops, rounding remainders, or tokens simply not declared in a given transaction's `erc20TokenAddresses` array — are excluded from both the Hinkal-level and the Emporium-level balance equations. An op such as `token.transfer(attackerAddress, token.balanceOf(address(this)))`, where `token` is not present in the caller's own `circomData.erc20TokenAddresses`, drains that balance with zero effect on any equality check, since neither `balancesBefore/After` (Emporium) nor `oldBalances/newBalances` (Hinkal) track that token at all.

This is the same class of defect as H01: instead of relying on a *fragile cached total* that misattributes deposits, Hinkal/Emporium relies on a *balance-diff equation scoped only to a declared token list*, and any value sitting outside that declared scope on the shared contract is unaccounted for and freely movable by an unprivileged caller.

### Impact Explanation
Any residual ERC20 balance accumulating on the Emporium contract (dust from swaps, partial fills, previously stuck outputs, or funds a legitimate user's transaction left behind because a token wasn't included in that tx's declared token set) is not the attacker's own shielded balance — it is protocol/other users' residual value. An unprivileged caller can construct a `transact()` call that routes to Emporium with a stateless op transferring that balance to themselves, which is unauthorized asset movement / theft of value that was never counted in the balance equation the protocol relies on to guarantee correctness. This falls under High severity ("theft ... of protocol/relay fees, temporary freezing of user funds, executing calls or moving assets ... never authorised") and can rise to Critical if the drained token was itself in-flight user value awaiting a UTXO.

### Likelihood Explanation
Likelihood is moderate: it requires the Emporium contract to actually hold a non-zero balance of some ERC20 token that is not included in the current transaction's `erc20TokenAddresses` array. Given Emporium is designed to route arbitrary DeFi calls (swaps, LI.FI, etc.) where output amounts, dust, and unexpected token transfers are common, non-zero incidental balances are a realistic and recurring occurrence. Any EOA can trigger the drain unilaterally once such a balance exists, with no privileged role required.

### Recommendation
- Do not scope the pre/post balance equality check to only the caller-declared `erc20TokenAddresses`; instead, track and reconcile balances for every token the ops touch, or forbid ops from targeting arbitrary ERC20 contracts unless explicitly declared in `circomData.erc20TokenAddresses` with a corresponding equality check.
- Require signature verification (`verifyWallet`) unconditionally, rather than skipping it whenever `stack.signerAddress == address(0)`, and disallow "stateless" ops from calling `endpoint`s that are token contracts unless whitelisted.
- Sweep any residual Emporium balance atomically at the end of `runAction` back into the balance equation (e.g., revert if any tracked token balance differs from expected, and force any incidental leftover to be attributed to a specific commitment rather than silently sitting on the contract).

### Proof of Concept
1. Some prior legitimate `transact()` call (or a partially-completed op sequence) leaves `D` units of `TOKEN_X` sitting on the Emporium contract, where `TOKEN_X` was not part of that transaction's `circomData.erc20TokenAddresses`, or is left over due to rounding/dust after a swap.
2. Attacker (any unprivileged EOA) submits a valid `transact()` call routed through the Emporium external action (`externalActionId == HINKAL_EMPORIUM_ACTION_ID`), with `circomData.erc20TokenAddresses` deliberately excluding `TOKEN_X`.
3. `circomData.externalActionData.externalActionMetadata` encodes an `EmporiumStack` with `signerAddress = address(0)` (skips signature check) and one stateless `EmporiumOperation`: `endpoint = TOKEN_X`, `callData = abi.encodeCall(IERC20.transfer, (attacker, D))`.
4. `EmporiumUpgradeable.runAction` executes the op via `op.endpoint.call(op.callData)` at [5](#0-4) , successfully transferring `D` units of `TOKEN_X` to the attacker.
5. Because `TOKEN_X` is absent from `circomData.erc20TokenAddresses`, neither the `balancesBefore/balancesAfter` loop in `runAction` nor the `oldBalances/newBalances` loop in `Hinkal.transact()` observe or reject this transfer; the transaction completes successfully, and the attacker has stolen `D` units of `TOKEN_X` from the shared Emporium contract with no corresponding debit to any UTXO or shielded balance of theirs.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L314-316)
```text
        if (stack.signerAddress == address(0)) {
            return;
        }
```
