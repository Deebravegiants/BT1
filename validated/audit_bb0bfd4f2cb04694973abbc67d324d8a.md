### Title
Unbounded router approval in `LifiExternalAction`/`ExternalActionSwap` lets an attacker-controlled swap drain stray token balances via the router - (File: `contracts/external-actions/swaps/LifiExternalAction.sol`)

### Summary
`LifiExternalAction.callRouter` grants the LI.FI `router` an **unlimited, persistent** ERC-20 allowance on `inputToken` (`approveUnlimited`) instead of an allowance bounded to the swap's `inputAmount`, and then executes `router.call(externalActionMetadata)` where `externalActionMetadata` is **fully attacker-chosen calldata** (any user can trigger a swap for their own tiny deposit and craft this payload). Because the allowance is unbounded and persists across transactions, and the call target/arguments passed to the already-approved `router` are entirely user supplied, an attacker can construct calldata that instructs the router to pull far more of `inputToken` than the amount they actually deposited — up to the contract's full balance of that token — and route the proceeds to an address of their choosing instead of back to `LifiExternalAction`.

### Finding Description
`ExternalActionSwap.swap()` is invoked by `Hinkal._externalTransact` only after Hinkal has pushed `inputAmount` of `inputToken` into `LifiExternalAction`: [1](#0-0) 

Inside `LifiExternalAction.callRouter`, the contract measures the swap output purely via balance-diff of `outputToken`, but the *input side* is protected only by an ERC-20 `approve`, and that approve is unlimited rather than scoped to `inputAmount`: [2](#0-1) 

`approveUnlimited` sets the router's allowance to `type(uint256).max` and leaves it there for future calls as well: [3](#0-2) 

Crucially, `externalActionMetadata` — the exact bytes sent to `router.call(...)` — is chosen by whoever submits the `transact()` call and is only checked for internal self-consistency (it is hashed into `calldataHash`, which is itself a public circuit input), not restricted in content: [4](#0-3) 

A user does **not** need to own any pre-existing shielded UTXO to reach this code path: `MainEVMCircuit`'s nullifier/root checks are only "enabled" when `inAmounts[i][j] != 0`, so a fresh deposit (`inAmounts = 0`) with a self-generated valid proof is sufficient: [5](#0-4) 

This means: any EOA can deposit a minimal amount of `inputToken`, trigger `LifiExternalAction.swap()`, and supply `externalActionMetadata` that calls a legitimate router function (e.g. a generic pull-then-swap entrypoint) specifying an amount to pull that is larger than what they deposited, and a destination that is not `LifiExternalAction`. Because the router already holds `type(uint256).max` allowance on `inputToken` from this or any earlier swap using the same token, the router can successfully `transferFrom` the **entire current balance** of `inputToken` held by `LifiExternalAction` — which can include dust/leftovers from earlier partial-fill swaps or funds momentarily resident there — and send it to the attacker instead of back into the contract.

This breaks the equality the report's bug-class targets: value that is moved out of `LifiExternalAction` by the router is not bounded by, or reconciled against, the specific `deltaAmounts`/`inputAmount` that Hinkal's balance equation in `transact()` expects: [6](#0-5) 
That equation only checks the *net* balance change of `LifiExternalAction` as observed from Hinkal's perspective for the attacker's own transaction — it has no way to see or prevent a call that drains balance belonging to residual/other funds via the unlimited allowance, since the drain happens entirely inside the router call using an allowance set in a *previous* (already-settled) transaction.

### Impact Explanation
Any stray/leftover balance of a given `inputToken` sitting in `LifiExternalAction` (e.g., dust from partial-fill swaps, timing windows between transactions, or protocol/relay fee tokens momentarily held) can be stolen by any unprivileged user who triggers a new swap for that same token and supplies malicious `externalActionMetadata`. This is theft of protocol funds/other users' in-flight funds via unauthorized token movement (a `transferFrom`/wallet op that was never authorised by the depositing party for that amount) — matching the High/Critical impact bar (theft of protocol/relay funds, or theft of shielded user funds if the residual balance belonged to another user's in-flight transaction).

### Likelihood Explanation
Likelihood depends on how frequently token dust/residual balances actually accumulate in `LifiExternalAction` (partial fills, slippage, or race conditions across near-simultaneous swaps of the same token) — this is plausible for a DEX-aggregator router integration but I could not directly verify from the indexed contracts whether the router routinely leaves partial-fill dust, since the router itself (LI.FI Diamond) is out-of-repo. The root-cause weakness — unbounded, non-`inputAmount`-scoped, persistent approval granted to a contract that is then invoked with fully attacker-controlled calldata — is present regardless, and is exploitable as soon as **any** non-zero balance of the given `inputToken` exists in `LifiExternalAction` at call time that exceeds the attacker's own deposit.

### Recommendation
- Scope the router approval to exactly `inputAmount` per swap (revoke/reset after use) instead of granting `type(uint256).max`, so the router can never pull more than what was deposited for that specific swap.
- Alternatively/additionally, verify the *pre-swap* balance of `inputToken` before approving/calling the router and assert that the post-call balance decreased by no more than `inputAmount`, mirroring the balance-diff check already used for `outputToken`.

### Proof of Concept
1. Attacker deposits `1 wei` of token `X` via `Hinkal.transact()` with `externalActionId` pointing to `LifiExternalAction`, using a fresh (input-UTXO-less) proof since `inAmounts = 0` disables the nullifier/root checks.
2. Hinkal pushes `1 wei` of `X` into `LifiExternalAction` and calls `runAction` → `swap()`.
3. `callRouter` calls `approveUnlimited(X, router)`; if the router already had (from an earlier swap using `X`) or now gets `type(uint256).max` allowance on `X`.
4. Attacker's `externalActionMetadata` calls a legitimate router entrypoint (e.g. a pull-and-swap function) specifying `amount = currentBalanceOf(X, LifiExternalAction)` (which may be `> 1 wei` due to residual dust) and `recipient = attacker`.
5. Router executes `transferFrom(LifiExternalAction, ..., amount)` under the unlimited allowance, pulling the full stray balance of `X`, and routes proceeds to the attacker's address rather than back to `LifiExternalAction`.
6. `swappedAmount` computed from `outputToken` balance diff on `LifiExternalAction` is unaffected/near-zero for this attacker's own trade, so the transaction completes without reverting, while the attacker has extracted the extra `X` balance that belonged to the protocol/other in-flight users.

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

**File:** contracts/CircomDataBuilder.sol (L20-35)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }
```

**File:** circuits/MainEVMCircuit.circom (L144-149)
```text
        // 5) Checking that transaction root hash is legit
        calcEqual[i][j] = ForceEqualIfEnabled();
        calcEqual[i][j].in[0] <== calcTransactionRootHash[i][j].rootHash;
        calcEqual[i][j].in[1] <== rootHashHinkal;
        calcEqual[i][j].enabled <== inAmounts[i][j];
        inTotal += inAmounts[i][j];
```
