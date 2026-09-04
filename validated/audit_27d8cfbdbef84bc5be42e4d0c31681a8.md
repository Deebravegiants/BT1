### Title
Missing input-token balance invariant in `LifiExternalAction.callRouter`/`ExternalActionSwap.swap` allows stranded residual to be later drained by any caller - ([File: contracts/external-actions/swaps/LifiExternalAction.sol])

### Summary
`LifiExternalAction.callRouter` grants the LI.FI router an unlimited, persistent `approveUnlimited` allowance and then executes attacker-supplied `externalActionMetadata` against that router, measuring success purely by the *output* token balance delta. It never checks that the *input* token balance of the contract actually decreased by `inputAmount`. Because `externalActionMetadata` is not bound by the circuit or by any on-chain check to the `deltaAmounts`/`inputAmount` value, an attacker can craft calldata that under-consumes the approved input token in one transaction, stranding a residual balance in `LifiExternalAction`, and then in a later transaction craft calldata that pulls more than their own `inputAmount` (using the still-standing max allowance) to sweep the stranded residual into their own output/UTXO.

### Finding Description
The broken equality is:

`inputTokenBalance(LifiExternalAction)_before - inputTokenBalance(LifiExternalAction)_after == inputAmount == -deltaAmountChanges[0]`

This equality is never enforced anywhere in the call path. Trace:

1. `Hinkal._externalTransact` computes `deltaAmountChanges[0]` from the prover-supplied `circomData` and, because it is negative, transfers `inputAmount = uint256(-deltaAmountChanges[0])` of `inputToken` to `LifiExternalAction` via `transferERC20TokenOrETH`: [1](#0-0) 
2. `IExternalActionV2.runAction` → `ExternalActionSwap.swap` recomputes `inputAmount` the same way and calls `callRouter(inputToken, inputAmount, outputToken, circomData.externalActionData.externalActionMetadata)`, an entirely attacker-controlled byte string: [2](#0-1) 
3. `LifiExternalAction.callRouter` calls `approveUnlimited(inputToken, router)` — which only re-approves if current allowance is below `type(uint256).max/2`, otherwise leaves the existing max allowance in place — and then blindly forwards `router.call(externalActionMetadata)`. `swappedAmount` is computed solely as the *output* token balance delta; the input token's balance is never inspected: [3](#0-2)  and [4](#0-3) 
4. Back in `swap`, the credited UTXO amount to the caller is derived purely from `swappedAmount` (the output-token delta): [5](#0-4) 

Because `externalActionMetadata` is free-form calldata forwarded to a fixed but generic multi-purpose router, and it is not referenced anywhere in the circuit (`circuits/MainEVMCircuit*.circom` contain no constraint over `externalActionMetadata`), nothing ties the amount the router actually pulls to `inputAmount`/`deltaAmountChanges[0]`. A first attacker can craft calldata for a swap that only consumes part of `inputAmount`, leaving the rest as an ERC20 balance sitting in `LifiExternalAction` while the router keeps max allowance over it. A subsequent (or the same) attacker can then submit a second `Hinkal.transact` with a smaller declared `inputAmount` but calldata that instructs the router to pull `their inputAmount + the stranded residual` (both amounts are already approved to the router from the contract's unlimited allowance) and swap all of it, so `swappedAmount` (output token delta) now reflects the extra stolen residual, which is credited entirely to the second attacker's UTXO via `transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal)`.

None of the existing guards prevent this: `performHinkalChecks`/`dimensionsCheck` validate proof structure and dimension bounds, not the semantic content of `externalActionMetadata`; the circuit constraints (`inTotal + amountChanges === outTotal`, `OverflowPreventer`) only constrain the prover's own declared `amountChanges`, not what the router actually executes; the Hinkal-level slippage check (`balanceDif >= slippageValues[i]`) protects the depositor's own transaction against under-delivery of output token but does nothing to prevent input-token residue from being stranded or later drained, since that residue never shows up as a negative balance difference for anyone.

### Impact Explanation
Critical — direct theft of another user's in-flight/shielded funds. The first (victim) user's input tokens are stranded inside `LifiExternalAction` instead of being fully converted and credited to their UTXO; a second, unrelated unprivileged attacker can, in a later transaction, redirect that stranded balance into their own credited UTXO by exploiting the unlimited allowance and the unconstrained `externalActionMetadata` field. This is repeatable for every subsequent swap through `LifiExternalAction` for the same `inputToken`/router pair, since `approveUnlimited` re-establishes/keeps a near-infinite allowance each time.

### Likelihood Explanation
- Requires only two ordinary `Hinkal.transact` calls from unprivileged accounts (no special role required) and control over `externalActionMetadata`, which is entirely attacker-supplied and unconstrained by circuit or contract.
- Requires a router (LI.FI diamond or equivalent) accepting calldata whose specified swap amount can differ from what a "polite" caller would use, and pulling only that specified amount via the already-granted allowance — a normal feature of generic swap-aggregator calldata, not a router defect being relied upon.
- The attacker's cost is just gas plus the ability to construct valid LI.FI/router calldata targeting the fixed `router` address; feasible for any sophisticated caller.
- Fully repeatable across transactions/tokens as long as any prior transaction under-consumed its approved input amount (accidentally or maliciously).

### Recommendation
In `LifiExternalAction.callRouter` (and generally in `ExternalActionSwap.swap`), assert that the input token balance of the contract decreased by exactly `inputAmount` after the router call (or refund/revert on any leftover), and avoid leaving persistent unlimited allowances to the router across transactions — e.g., approve exactly `inputAmount` before the call and reset the allowance to zero afterward regardless of how much the router actually consumed. This closes both the under-consumption stranding and the over-consumption draining paths.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, and `LifiExternalAction` pointed at a mock router.
2. Configure the mock router so that, given calldata A, it only `transferFrom`s half of the approved `inputAmount` of `inputToken` and mints/transfers the corresponding `outputToken` back.
3. As attacker #1, deposit `inputToken`, generate a valid proof declaring `deltaAmountChanges[0] = -inputAmount` for a swap `inputToken -> outputToken` using calldata A, call `Hinkal.transact`.
   - Assert `IERC20(inputToken).balanceOf(address(lifiExternalAction)) == inputAmount / 2` (stranded residual) and `IERC20(inputToken).allowance(address(lifiExternalAction), router) >= type(uint256).max/2`.
4. As attacker #2, deposit a small amount of `inputToken`, generate a valid proof declaring `deltaAmountChanges[0] = -smallAmount`, but craft calldata B for the mock router that pulls `smallAmount + residual` (using the standing allowance) and swaps all of it to `outputToken`.
   - Call `Hinkal.transact` with this proof/calldata.
   - Assert attacker #2's minted UTXO `amount` (or the credited `outputToken` transfer to attacker #2) is greater than what `smallAmount` alone would have produced, and equals the value corresponding to `smallAmount + residual` minus fees — demonstrating theft of attacker #1's stranded residual.
   - Assert `IERC20(inputToken).balanceOf(address(lifiExternalAction))` returns to 0 after this second transaction, confirming the residual was fully drained into attacker #2's credited output.

### Citations

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
