### Title
Unbounded LI.FI router pull via attacker-crafted `externalActionMetadata` combined with standing `approveUnlimited` allowance lets an attacker drain `LifiExternalAction`'s residual token balance into their own UTXO - (File: `contracts/external-actions/swaps/LifiExternalAction.sol`)

### Summary
`LifiExternalAction.callRouter` grants `router` an unlimited, never-revoked ERC-20 allowance via `TransfererBase.approveUnlimited` and then executes fully attacker-supplied calldata (`externalActionMetadata`) against `router` with no constraint tying the amount the router actually pulls to the attacker's own `inputAmount = uint256(-deltaAmounts[0])`. Because `swappedAmount` (and thus the attacker's minted output UTXO) is derived purely from the output-token balance diff, and Hinkal's own balance-equality check in `transact` is self-referential for swap outputs, any residual `inputToken` sitting on `LifiExternalAction` from a prior transaction can be pulled by the router and converted into attacker-controlled value with only a trivial deposit of the attacker's own funds.

### Finding Description
The equality that must hold and is broken: `amount of inputToken debited from LifiExternalAction by router == inputAmount == uint256(-deltaAmounts[0])` (the amount Hinkal actually moved into `LifiExternalAction` for this specific transaction, tracked by `deltaAmountChanges` in `Hinkal._externalTransact`, [1](#0-0) ). In reality there is no such constraint anywhere in the call path.

`callRouter` grants `router` a standing `type(uint256).max` allowance the first time it's used and never revokes it (`allowance < type(uint256).max/2` check means it typically only sets once and is left at max) [2](#0-1) , then executes `router.call(externalActionMetadata)` where `externalActionMetadata` is 100% attacker-controlled calldata coming straight from `circomData.externalActionData.externalActionMetadata` [3](#0-2) . The `inputAmount` parameter is only used for the native-ETH branch (`router.call{value: inputAmount}`); for ERC-20 it is not passed to the router at all — the router decides unilaterally, based on the attacker-crafted calldata, how much `inputToken` to `transferFrom` `LifiExternalAction`, bounded only by the unlimited allowance and `LifiExternalAction`'s actual token balance.

`swappedAmount` is computed as a pure balance diff: `getERC20OrETHBalance(outputToken) - balanceBefore` [4](#0-3) , and the whole (`swappedAmount - fees`) is minted straight into the attacker's own UTXO in `ExternalActionSwap.swap` [5](#0-4) .

Critically, Hinkal's own top-level accounting check does not prevent this because it is self-referential for the swap's output token: `balanceDif` is measured on the **Hinkal contract**, and `utxoAmount` is summed directly from the `utxoSet` that `LifiExternalAction` itself returned, so the check `balanceDif == amountChanges[i] + utxoAmount` reduces to a tautology once `amountChanges[1] == 0` for the output leg (the normal, expected case for a swap output) [6](#0-5) . There is no ceiling on `swappedAmount`/`utxoAmount` anywhere in this equation — any value the external action reports is accepted. The `slippageValues[i]` check is a floor (`balanceDif >= slippageValues[i]`), not a cap, so it does not block an unexpectedly large output [7](#0-6) .

Exploit flow:
1. Precondition: `LifiExternalAction` holds a residual balance of `inputToken` left over from a prior swap (e.g., a partial-fill LI.FI route that didn't consume the full approved/transferred amount — there is no sweep/refund of leftover input token in `ExternalActionSwap.swap`), and `router` already holds `type(uint256).max` allowance on that token from that prior swap's `approveUnlimited` call.
2. Attacker deposits a trivial amount of `inputToken` of their own via `Hinkal.transact`, proving a small `deltaAmounts[0]`.
3. Attacker crafts `externalActionMetadata` (raw LI.FI router calldata) that instructs `router` to pull an amount from `LifiExternalAction` far exceeding the attacker's own trivially-deposited `inputAmount`, consuming the residual balance too (allowed, since allowance is unlimited and balance is sufficient).
4. `router` swaps the larger pulled amount and returns a correspondingly larger amount of `outputToken` to `LifiExternalAction`.
5. `swappedAmount` reflects this inflated output; it is transferred to `msg.sender` (Hinkal) and turned into a UTXO fully controlled by the attacker's `stealthAddressStructure`.
6. Hinkal's balance-diff equation trivially passes because it re-derives `utxoAmount` from the same `utxoSet` the action returned.

### Impact Explanation
This is theft of protocol-parked residual/stranded tokens (value that legitimately belongs to the protocol/other users' unswept dust) and its conversion into attacker-controlled shielded UTXO value with no backing deposit from the attacker for the excess portion. This matches Critical: "direct theft of shielded or in-flight user funds ... minting shielded value without backing," since the resulting UTXO amount for the attacker exceeds what their own `amountChanges`/proof actually committed to spending. It is repeatable any time residual `inputToken` accumulates on `LifiExternalAction`.

### Likelihood Explanation
Preconditions: (1) `router` must already have been granted the unlimited allowance (happens automatically on the first ERC-20 swap for that token), and (2) `LifiExternalAction` must hold a non-zero residual balance of `inputToken` (plausible via partial-fill/multi-hop LI.FI routes that don't consume 100% of the approved amount, or dust from rounding in prior swaps). The attacker needs zero privileges — only the ability to craft `externalActionMetadata` and to submit a valid proof for their own trivial deposit, both explicitly within the stated attacker capabilities. Cost is minimal (gas + trivial deposit); the attack is repeatable every time residual balance reappears.

### Recommendation
Do not rely purely on post-call balance diff to determine `swappedAmount`/UTXO amount. Either (a) cap the router pull by using `SafeERC20.forceApprove` scoped exactly to `inputAmount` per call instead of a standing unlimited approval, and verify `IERC20(inputToken).balanceOf(address(this))` decreased by exactly `inputAmount` after the router call, or (b) track and net out any pre-existing residual balance before the swap so it can never be attributed to the current caller's `swappedAmount`, and add an explicit assertion that `inputToken` balance drawn down by the router does not exceed `inputAmount`.

### Proof of Concept
Foundry test outline:
1. Deploy `LifiExternalAction` with a mock router and mock ERC-20 tokens (`inputToken`, `outputToken`).
2. Simulate a "prior legitimate swap": call `runAction`/`swap` once so `approveUnlimited` sets `router` allowance to `type(uint256).max`; have the mock router's calldata pull less than the full transferred `inputAmount`, leaving a residual `inputToken` balance sitting on `LifiExternalAction` (seed this residual directly via `deal`/`transfer` to `LifiExternalAction` to make the precondition explicit).
3. As attacker, call `Hinkal.transact` (or `LifiExternalAction.runAction` directly bypassing the proof layer to isolate this contract-level bug) with a trivial `inputAmount` (e.g., 1 wei) and `externalActionMetadata` encoding a mock-router call that does `IERC20(inputToken).transferFrom(LifiExternalAction, router, inputAmount + residualBalance)` and credits `outputToken` proportionally.
4. Assert: `swappedAmount` returned exceeds what `inputAmount` alone should have produced; assert attacker's final UTXO `amount` (`amountToSendToHinkal`) is unbacked, i.e., `amountToSendToHinkal > f(inputAmount)` while `circomData.amountChanges[1] == 0`, proving the equality `tokens pulled from LifiExternalAction == inputAmount` is violated and no on-chain check (`balanceDif == amountChanges[i] + utxoAmount`) rejects it.

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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-101)
```text
        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );

        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );

        if (circomData.feeStructure.feeToken == outputToken) {
            sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
        } else {
            sendToRelay(
                circomData.relay,
                relayFee,
                circomData.feeStructure.feeToken
            );
            sendToRelay(circomData.relay, hinkalFee, outputToken);
        }

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
