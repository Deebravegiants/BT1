### Title
Unlimited standing router approval + unchecked router calldata lets a caller drain a prior swap's stranded input-token dust from LifiExternalAction into their own output UTXO - ([File: contracts/external-actions/swaps/LifiExternalAction.sol])

### Summary
`LifiExternalAction.callRouter` grants the LI.FI router an unlimited, never-reset ERC20 approval via `approveUnlimited` and then blindly executes `router.call(externalActionMetadata)`, an opaque, fully attacker-crafted blob. Neither `ExternalActionSwap.swap` nor `Hinkal._externalTransact`/`Hinkal.transact` verify that the amount the router actually pulls from `LifiExternalAction` equals the `inputAmount` (`-deltaAmounts[0]`) allocated for that transaction, so any inputToken left stranded in `LifiExternalAction` from a prior swap (e.g. a partial fill that didn't consume the full transferred amount) can be pulled by a later, unrelated caller through the standing approval and converted into extra output credited to that caller's own UTXO.

### Finding Description
The invariant that should hold is: *tokens pulled from `LifiExternalAction` by the router in this call == `-deltaAmounts[0]` transferred into `LifiExternalAction` for this call*. Nothing enforces this equality.

- `Hinkal._externalTransact` transfers exactly `uint256(-deltaAmountChanges[0])` of the input token from `Hinkal` to `LifiExternalAction` and then calls `runAction` [1](#0-0) .
- `ExternalActionSwap.swap` computes `inputAmount = uint256(-deltaAmounts[0])` but never checks how much of it is actually consumed by the router; it only measures the *output* token balance delta as `swappedAmount` [2](#0-1) .
- `LifiExternalAction.callRouter` calls `approveUnlimited(inputToken, router)`, which only tops up the allowance to `type(uint256).max` and never resets it back to zero after the swap, then executes `router.call(externalActionMetadata)` with attacker-supplied calldata and no post-call check that its own inputToken balance returned to zero [3](#0-2) , [4](#0-3) .
- The Hinkal-side balance equality (`balanceDif == amountChanges[i] + utxoAmount`) is checked only against `Hinkal`'s own balance, not `LifiExternalAction`'s [5](#0-4) . For the output token, `utxoAmount` is derived directly from the swap's own measured `amountToSendToHinkal` (`utxoSet[0].amount = amountToSendToHinkal`), so this check is tautological and provides no independent bound on the swap's output value [6](#0-5) .
- The ZK circuit constrains only the shielded pool's own UTXO set (`inTotal + amountChanges[i] === outTotal`) [7](#0-6) ; the on-chain commitment produced by the swap action is inserted separately via `createOnchainCommitment(utxoSet[j], ...)` and is not bound by this equation, only by `checkOnchainCreation` requiring `amountChanges[i] == 0` for onChainCreation entries [8](#0-7) .

Exploit flow:
1. Some transaction (attacker's own or a normal user's) swaps token X, and the LI.FI route consumes less than the `inputAmount` transferred into `LifiExternalAction` (e.g., partial fill), leaving X-token dust stranded there under a standing max approval to the router.
2. Attacker submits `transact` with `externalActionData.externalActionId` = LifiExternalAction, `erc20TokenAddresses[0] = X`, a small legitimate `deltaAmounts[0]`, and a crafted `externalActionMetadata` whose embedded swap amount instructs the router to pull `deltaAmounts[0] + dust` from `LifiExternalAction` (already approved for `type(uint256).max`).
3. `callRouter` measures `swappedAmount` as the resulting larger output-token delta; `swap()` sends the inflated `amountToSendToHinkal` to `Hinkal`, which mints it as the attacker's own on-chain UTXO commitment.
4. `Hinkal.transact`'s balance checks pass trivially because they only compare Hinkal's own balance movement against the swap's self-reported UTXO amount — they never verify the amount `LifiExternalAction` actually surrendered to the router matched what was allocated for this transaction.

### Impact Explanation
The attacker mints a private UTXO worth more than the value they put in, funded by dust that belonged to a different, unrelated prior transaction/user and was never returned to them. This is direct theft of stranded protocol/relay- or user-attributable residual funds and is repeatable every time dust accumulates for a given token, meeting the Critical bar (theft of in-flight/shielded user funds) or at minimum High (theft of protocol/relay-held residual funds), depending on whose dust is present.

### Likelihood Explanation
Preconditions: (a) some prior swap leaves the input token partially unconsumed inside `LifiExternalAction` (plausible with partial-fill/aggregator routes, or can be engineered by the attacker themselves in a first, self-funded transaction), and (b) the attacker knows/controls the router calldata format well enough to specify a larger `fromAmount` than their own allocated `deltaAmounts[0]`. Given `externalActionMetadata` is entirely attacker-supplied opaque calldata forwarded verbatim to the router, and the standing unlimited approval is never reset, this is straightforward and cheap to execute repeatedly for any token pair that accumulates dust.

### Recommendation
- Never grant unlimited, persistent approvals to the router; approve exactly `inputAmount` before the call and reset to zero after, so a stale approval cannot be reused across unrelated transactions.
- Assert `LifiExternalAction`'s inputToken balance decreased by exactly `inputAmount` (or by no more than `inputAmount`) after `router.call`, reverting otherwise.
- Add an explicit "no stranded balance" invariant: after `swap()`, require `getERC20OrETHBalance(inputToken)` on `LifiExternalAction` be unchanged from before the transaction started (accounting only for `inputAmount` in/out), and sweep any unconsumed remainder back to the depositor rather than letting it sit under an active router approval.

### Proof of Concept
Foundry fork test plan:
1. Deploy `Hinkal`, `LifiExternalAction` pointed at a real/forked LI.FI router, register the action.
2. Tx1 (victim or attacker-funded setup): perform a normal shielded swap of token X→Y through `LifiExternalAction`, using router calldata that intentionally/naturally consumes less than the transferred `inputAmount` of X, leaving e.g. `100e18` of X stuck in `LifiExternalAction` with the router still holding `type(uint256).max` allowance over it. Assert `IERC20(X).balanceOf(LifiExternalAction) == 100e18` and `IERC20(X).allowance(LifiExternalAction, router) > 100e18`.
3. Tx2 (attacker, unrelated): submit `transact` with a locally-generated valid proof for a small legitimate swap of X→Y with `deltaAmounts[0] = 10e18`, but with `externalActionMetadata` crafted so the router's `fromAmount` = `110e18` (their `10e18` + the `100e18` dust).
4. Assert: `Hinkal`'s balanceDif checks pass (transaction succeeds), and the attacker's newly created on-chain UTXO (`amountToSendToHinkal`/`swappedAmount`) reflects output for `110e18` of input rather than the `10e18` they actually contributed — i.e., `swappedAmount` measured on-chain exceeds the amount a swap of just `10e18` should have produced, while `IERC20(X).balanceOf(LifiExternalAction)` drops to `0`, proving the extra `100e18` of stranded X (not committed in `circomData.amountChanges`) was drained and monetized into the attacker's private balance.

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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L91-101)
```text
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

**File:** circuits/MainEVMCircuit.circom (L152-169)
```text
    for(var j=0; j< outputCount; j++) {
      calcOutCommitment[i][j] = OriginalCommitmentCalculator();
      calcOutCommitment[i][j].amount <== outAmounts[i][j]; // if outAmount is negative, than this line will throw error
      calcOutCommitment[i][j].erc20TokenAddress <== erc20TokenAddresses[i];
      calcOutCommitment[i][j].publicKey <== outPublicKeys[i][j];
      calcOutCommitment[i][j].timeStamp <== outTimeStamp;

      // Checking that output commitment is legit
      calcOutCommitment[i][j].out === outCommitments[i][j];

      preventOutOverflow[i][j] = OverflowPreventer(outputCount);
      preventOutOverflow[i][j].in <== outAmounts[i][j];
      outTotal += outAmounts[i][j];
    }

      // for each token type, the sum of refund and swapped amount should be equal to the sum of input amounts
      inTotal + amountChanges[i] === outTotal;
	}
```

**File:** contracts/HinkalHelper.sol (L181-200)
```text
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
```
