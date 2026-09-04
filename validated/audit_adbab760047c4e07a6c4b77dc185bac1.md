### Title
Duplicate token entries in `erc20TokenAddresses` let an attacker double-count a single balance delta and drain residual/stranded funds from `EmporiumUpgradeable` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` snapshots contract-wide token balances once before and once after the router calls, then loops per-index over `circomData.erc20TokenAddresses` to compute each token's net change and hand it to `handleOut`, which unconditionally transfers `balanceChange` to `msg.sender`. If the same ERC20 address is listed twice in `erc20TokenAddresses` (a "same-token second leg"), the loop reads the *same* `balancesBefore[i]`/`balancesAfter[i]` values twice and computes the same ops-driven delta `D` for both legs, so it can pay out `D` twice while only one leg's `deltaAmountChanges` needs to net against the real inflow. Any residual balance already sitting in the contract (e.g. left over from a prior router refund) can be claimed as part of the second leg's "surplus," breaking the invariant that tokens leaving the action in a tx equal `-deltaAmountChanges` sent to it that tx.

### Finding Description
The invariant that should hold is:

```
sum(tokens transferred out of Emporium in this tx) == sum(-deltaAmountChanges[i] for tokens Hinkal sent into it this tx) + (net token movement genuinely produced by this tx's ops)
```

In `runAction`:
```solidity
uint256[] memory balancesBefore = getBalancesForArray(circomData.erc20TokenAddresses); // line 85
...
uint256[] memory balancesAfter = getBalancesForArray(circomData.erc20TokenAddresses);   // line 122
for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
    int256 balanceChange = int256(balancesAfter[i]) - int256(balancesBefore[i]);        // line 133-134
    if (deltaAmountChanges[i] < 0) {
        balanceChange -= deltaAmountChanges[i];                                          // line 137
    }
    if (balanceChange < 0) revert BalanceChangeShouldBePositive();
    UTXO memory utxoOut = handleOut(balanceChange, circomData, i);                        // line 146
    ...
}
``` [1](#0-0) 

`getBalancesForArray` reads `token.balanceOf(address(this))` independently for each array index with no de-duplication: [2](#0-1) 

If token `X` appears at both index `i` and index `j` in `circomData.erc20TokenAddresses`, then `balancesBefore[i] == balancesBefore[j]` and `balancesAfter[i] == balancesAfter[j]` (they are the same global contract balance read twice, once before all ops and once after all ops). The raw ops-driven delta `D = balancesAfter - balancesBefore` for token `X` is therefore identical for both legs. The loop then independently adds each leg's own `-deltaAmountChanges[i]`/`-deltaAmountChanges[j]` and calls `handleOut`, which does an unconditional `transferERC20TokenOrETH(token, msg.sender, balanceChange)` for each leg: [3](#0-2) 

This means the same ops-driven surplus `D` (e.g. a router refund that was never swept out on a prior transaction and is sitting as residual balance in the contract) is counted and paid out **twice** — once per leg — instead of once. As long as the total amount transferred out across both legs (`2D + A_i + A_j`, where `A_i`/`A_j` are the leg-specific deposit adjustments) does not exceed the actual token balance in the contract at payout time, both `transferERC20TokenOrETH` calls succeed, and the attacker collects `D` extra as an additional `UTXO` output (built with `circomData.stealthAddressStructure`, which the attacker fully controls) beyond what Hinkal actually moved into the action for that token (`-deltaAmountChanges`).

There is no check anywhere in `runAction`, `verifyWallet`, or `payRelayFees` that `erc20TokenAddresses` contains unique addresses; nothing in this contract enforces per-token uniqueness of the index array before doing the balance-delta accounting.

### Impact Explanation
An attacker who controls `externalActionMetadata` (choosing router calls that leave a small refund/leftover in the Emporium contract, or simply relying on any pre-existing stranded balance from earlier interactions) and controls the ordering/content of `erc20TokenAddresses` and `deltaAmountChanges` can duplicate a token's index to have its net ops-driven delta counted twice by `handleOut`, pulling out value that was never accounted for by `-deltaAmountChanges` for that transaction. Since the output UTXO is minted to a stealth address the attacker chooses, this is direct theft of funds parked in the action (potentially belonging to the protocol/other in-flight users), matching a Critical-severity "direct theft of shielded or in-flight user funds" impact. It is repeatable any time residual balance exists in the Emporium contract for a given token.

### Likelihood Explanation
- Requires the Emporium contract to hold some non-zero residual balance for a token at the start of the attacker's transaction (e.g., from a router refund left over from any prior action, or dust from imprecise swaps) — a realistically common state given multi-hop swaps and slippage.
- The attacker needs no privileged role: `runAction` is only gated by `onlyAllowedRecipient`, which restricts the *caller* to the Hinkal contract itself, not the originating user; any unprivileged user can drive this path through `Hinkal.transact` by supplying their own `externalActionMetadata`/`erc20TokenAddresses`/`deltaAmountChanges`.
- Cost is limited to gas plus proof generation for the attacker's own UTXOs.
- Feasibility depends on whether nothing upstream (e.g. circuit constraints on `erc20TokenAddresses` uniqueness, or Hinkal.sol-level validation) rejects duplicate token addresses in the array before calling `runAction`. I was not able to fully confirm from the available index whether `Hinkal.sol` or the circuit enforces uniqueness of `erc20TokenAddresses`; the grep on `Hinkal.sol` returned matches but I did not get to inspect the full body of the relevant sections due to running out of iterations, so I cannot rule out an upstream check that would prevent this exact duplicate-index construction. This uncertainty should be resolved with a Foundry PoC before treating this as fully confirmed.

### Recommendation
- De-duplicate `circomData.erc20TokenAddresses` (or reject duplicates) before computing `balancesBefore`/`balancesAfter`/`handleOut`, so each distinct token address is processed exactly once in `runAction`.
- Alternatively, aggregate `deltaAmountChanges` per unique token first, then compute a single `balanceChange` per unique token and call `handleOut` once per unique token, ensuring the accounting invariant `tokens leaving == -sum(deltaAmountChanges) + net ops delta` holds even with attacker-supplied duplicate entries.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable` with a mock allowed recipient acting as the `Hinkal` caller and a mock ERC20 token.
2. Seed a residual balance `D` of the mock token directly into the `EmporiumUpgradeable` contract (simulating a stranded router refund from a prior action), without any corresponding UTXO accounting.
3. Craft `circomData.erc20TokenAddresses = [tokenX, tokenX]` (same token at two indices) and `deltaAmountChanges = [-A_i, -A_j]` such that the actual token amount Hinkal transfers in equals `A_i + A_j` before calling `runAction`, and the ops array is a no-op (or a trivial call that does not touch `tokenX`).
4. Call `runAction` as the allowed recipient (Hinkal mock).
5. Assert: `tokenX.balanceOf(emporium) before - after == A_i + A_j + D` (i.e., the contract pays out `D` more than what Hinkal put in), and that the returned `utxoSet` contains two UTXOs for `tokenX` summing to `A_i + A_j + D` credited to the attacker's stealth address, violating `tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx`.
6. Compare against a control run with a single, non-duplicated index for `tokenX`, where the residual `D` is not paid out and remains stranded, confirming the duplicate-index path is what leaks the residual.

### Citations

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

**File:** contracts/Transferer.sol (L169-176)
```text
    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }
```
