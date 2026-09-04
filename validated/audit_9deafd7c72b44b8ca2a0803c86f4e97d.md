## Title
Unspent native-ETH sent to the swap router is not tracked or refunded, permanently stranding user funds in `ExternalActionSwap` / `LifiExternalAction` - (File: `contracts/external-actions/swaps/ExternalActionSwap.sol`, `contracts/external-actions/swaps/LifiExternalAction.sol`)

### Summary
`ExternalActionSwap.swap()` forwards the *entire* declared `inputAmount` (native ETH) to `LifiExternalAction.callRouter`, which passes it to the external LI.FI `router` via a raw `call{value: inputAmount}`. The only balance check performed afterwards is on `outputToken`; the contract never re-checks its own native ETH balance after the router call. If the router does not consume the full `inputAmount` and returns the difference (a normal DEX/bridge behavior, e.g. slippage protection or partial fill), that leftover ETH lands on the `ExternalActionSwap`/`LifiExternalAction` contract (which does accept ETH via its `receive()`), but is never captured, forwarded to Hinkal, or refunded to the depositor. It is permanently stuck in the contract with no sweep mechanism.

### Finding Description
`ExternalActionSwap.swap()` computes: [1](#0-0) 

It only measures `outputToken` balance before/after the router call inside `callRouter`: [2](#0-1) 

Note that `balanceBefore`/`swappedAmount` are computed exclusively on `outputToken`; the ETH (`inputToken`) balance of the contract is never re-checked after the low-level `router.call{value: inputAmount}(...)`. Any ETH the router returns via a plain transfer (accepted silently because `ExternalActionSwap` declares `receive() external payable {}`) is invisible to the accounting logic: [3](#0-2) 

Contrast this with `Hinkal`'s general balance equality, in which `deltaAmountChanges[i]` for the input token is computed once at the top level and is assumed to be *entirely* consumed by the external action: [4](#0-3) 

The full `inputAmount` (minus fee) is transferred out of `Hinkal` into the external action and treated as spent, without any accounting for a partial refund coming back from the target router. Because `swap()` only produces one `UTXO` for `outputToken`, there's no path by which leftover native ETH can be re-minted into a shielded UTXO or returned to `msg.sender` (Hinkal). It simply accumulates as a plain ETH balance on the `ExternalActionSwap`/`LifiExternalAction` contract, unlinked to any user's shielded balance, with no owner or public sweep function present in the contract (`TransfererBase`, `Transferer`, `ExternalActionBaseV2` expose no withdrawal/rescue function).

This is the same root cause identified in the external report: a contract that forwards ETH to a target and receives change back has no logic to route that change back to the rightful owner — the difference here is `ExternalActionSwap` does accept ETH (so it doesn't revert), but the unaccounted ETH is silently orphaned rather than causing a revert.

### Impact Explanation
This breaks the balance equality the protocol relies on: the circuit/Hinkal side already debited the user's shielded balance for the *full* `inputAmount`, but the external action never returns the unspent portion to any UTXO or to the relay/fee recipient. The stranded ETH is not recoverable by the user, the relay, or the protocol (no sweep function exists), constituting permanent freezing of a portion of user funds whenever the underlying router performs a partial-fill/refund. This qualifies as at least a High severity issue (temporary/permanent freezing of user funds), matching the severity uplift reasoning used in the original report, since `LifiExternalAction`/`ExternalActionSwap` is a routinely exercised external action path.

### Likelihood Explanation
Requires only a normal user swap request through the `LifiExternalAction`/`ExternalActionSwap` path where `inputToken == address(0)` (native ETH swap) and the LI.FI router (or whatever router is configured) performs a partial fill or applies slippage protection that refunds unused input ETH — a routine, non-adversarial occurrence for aggregator/router contracts, not requiring any privileged role or malicious relayer.

### Recommendation
Track the contract's native ETH balance before and after `router.call` in `LifiExternalAction.callRouter` (in addition to `outputToken`), and if `inputToken == address(0)`, include the actual consumed amount / leftover ETH in the accounting performed by `ExternalActionSwap.swap()`; either mint an additional UTXO for the leftover ETH back to the user's stealth address, or transfer it back to `msg.sender` (Hinkal) so it can be reconciled with the shielded balance, mirroring the approach used in `EmporiumUpgradeable.runAction`, which fully diff's balances for every token in `circomData.erc20TokenAddresses` rather than only the output token.

### Proof of Concept
1. User initiates a shielded swap through Hinkal specifying `erc20TokenAddresses = [address(0), outputToken]`, `amountChanges` reflecting `-inputAmount` for ETH.
2. Hinkal's `_externalTransact` transfers `inputAmount` ETH to `LifiExternalAction` and calls `runAction` → `swap()`.
3. `swap()` calls `callRouter`, which forwards the full `inputAmount` to the LI.FI `router` via `router.call{value: inputAmount}(externalActionMetadata)`.
4. The router only needs `inputAmount - delta` ETH to complete the swap (e.g., due to slippage protection or a partial-fill code path) and sends `delta` ETH back to `msg.sender`, which is the `LifiExternalAction` contract. The contract's `receive()` accepts it silently.
5. `swap()` measures only `outputToken` balance delta as `swappedAmount`; the `delta` ETH refund is never observed.
6. `swap()` completes, minting a UTXO only for `outputToken`. The `delta` ETH remains on the `LifiExternalAction`/`ExternalActionSwap` contract's balance permanently, inaccessible to the user, relay, or protocol.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L30-31)
```text

    receive() external payable {}
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L44-68)
```text
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
