I'll research the codebase for swap/quote handling logic similar to the described bug pattern before drawing any conclusions.This looks like a genuine and interesting bug pattern. Let me verify whether the swap `externalActionMetadata` calldata amount is ever checked against the circuit-proven `inputAmount`, and whether any rescue/allowance mechanism exists.### Title
Uncapped/unaccounted swap allowance lets any user drain leftover input-token dust from prior swaps in `LifiExternalAction` - (File: `contracts/external-actions/swaps/LifiExternalAction.sol`)

### Summary
`LifiExternalAction.callRouter` never enforces that the amount actually consumed by the LI.FI router matches the `inputAmount` that Hinkal computed and transferred in for that specific transaction. Combined with `approveUnlimited`, which grants the router `type(uint256).max` allowance over the *entire* contract balance rather than a per-call amount, any leftover input-token balance from a prior under-consuming swap becomes available to be pulled by a completely unrelated, later transaction. This is the same root cause as the reported Hashflow bug (a pre-computed/quoted amount is not enforced on-chain against what is actually consumed), except here it enables outright theft of another user's stuck funds rather than merely stranding them with the swap executor.

### Finding Description
For ERC-20 input swaps, `LifiExternalAction.callRouter` does: [1](#0-0) 

Note that the `inputAmount` parameter is only used in the native-ETH branch; for ERC-20 tokens it is completely unused. The actual amount pulled from the contract is whatever `externalActionMetadata` encodes for the router call, and the allowance granted via `approveUnlimited` is `type(uint256).max`, not scoped to the current transaction's `inputAmount`: [2](#0-1) 

Hinkal transfers exactly `inputAmount` (derived from `deltaAmountChanges`) into the `LifiExternalAction`/`ExternalActionSwap` contract before calling `runAction`: [3](#0-2) 

`ExternalActionSwap.swap` then calls `callRouter` and treats whatever balance delta occurred on `outputToken` as `swappedAmount`, without ever verifying that exactly `inputAmount` of `inputToken` was consumed: [4](#0-3) 

The outer balance equation in `Hinkal.transact` only checks the *Hinkal contract's own* balance delta against the user's declared `amountChanges`/UTXO amounts — it has no visibility into what happens to funds once they are inside `LifiExternalAction`: [5](#0-4) 

Because `externalActionMetadata` is fully attacker-chosen bytes forwarded verbatim to `router.call(...)`, and only its *hash* (not its numeric consistency with `inputAmount`) is checked via `calldataHash`/the EIP-712 signed message, a user's own transaction can leave `inputToken` dust behind (if the encoded router call consumes less than `inputAmount`). Since `approveUnlimited` leaves the router permanently approved for the contract's *whole* balance (not just the current call's `inputAmount`), that dust remains claimable. A later, unrelated but fully valid and self-signed transaction from a different user can encode `externalActionMetadata` that instructs the router to pull more `inputToken` than that user's own `inputAmount` — consuming the earlier dust too — producing a larger real `outputToken` balance increase. Because the circuit only enforces internal conservation of the *declared* `amountChanges`/UTXO totals (`inTotal + amountChanges[i] === outTotal` per token) and not any binding between `inputAmount` and the router's actual consumption, the attacker is free to declare a correspondingly larger `outputToken` UTXO for themselves, which will pass Hinkal's outer balance check because the real balance change now matches their inflated declaration: [6](#0-5) 

This breaks the equality that a user's shielded output must be backed only by that same user's consumed input: value belonging to a previous, unrelated transaction is silently absorbed into the balance equation of a later attacker's transaction.

### Impact Explanation
This is theft of another user's (or protocol's, if fees are involved) previously-deposited but under-consumed funds — an unbacked increase to the attacker's shielded balance funded by value that was never theirs. This matches the Critical-tier criteria: "direct theft of shielded or in-flight user funds" / "minting shielded value without backing." It also matches "value moved by Hinkal or an external action but not counted in the balance equation," since Hinkal's balance equation only checks its own contract's balance and never re-verifies what the external swap action actually consumed versus what it was given.

### Likelihood Explanation
Exploitation requires: (1) some transaction (the victim's, possibly triggered by legitimate slippage/rounding in an off-chain-built LI.FI calldata) leaves `inputToken` dust in `LifiExternalAction`, and (2) an attacker crafting their own valid, self-signed transaction whose `externalActionMetadata` requests a larger pull than their own `inputAmount`. Both steps are entirely achievable by an unprivileged EOA controlling their own proof/signature and calldata — no admin, relayer, or third-party key is needed. The severity depends on dust size accumulating, but the underlying missing invariant (no on-chain check tying router consumption to `inputAmount`) is a structural flaw, not a rare edge case.

### Recommendation
- In `LifiExternalAction.callRouter`, explicitly track and enforce that the router consumes exactly `inputAmount` of `inputToken` (e.g., check `balanceBefore - balanceAfter(inputToken) == inputAmount`, reverting otherwise), analogous to the recommended Hashflow fix of reverting when the actual amount used deviates from the expected one.
- Replace unconditional `approveUnlimited` with a per-call `approveERC20Token(inputToken, router, inputAmount)` so the router can never draw on unrelated balances left in the contract from other transactions.

### Proof of Concept
1. User A submits a `transact()` swap call where their off-chain-built `externalActionMetadata` (LI.FI router calldata) is constructed to swap only `inputAmount_A - d` of `inputToken` instead of the full `inputAmount_A` that Hinkal transferred into `LifiExternalAction` (see `contracts/Hinkal.sol:247-256`). The swap completes; `d` worth of `inputToken` remains stuck in `LifiExternalAction`, and User A's own accounting absorbs the loss (self-inflicted, not directly exploitable alone).
2. Attacker B, in a separate, fully valid, self-signed `transact()` call, sets `externalActionMetadata` to a router call that requests pulling `inputAmount_B + d` of `inputToken` (relying on `approveUnlimited`'s uncapped allowance, `contracts/TransfererBase.sol:32-43`, to let the router draw on the residual `d` sitting in `LifiExternalAction` from step 1).
3. `LifiExternalAction.callRouter` performs no check that only `inputAmount_B` was consumed (`contracts/external-actions/swaps/LifiExternalAction.sol:16-36`), so the swap succeeds and yields more `outputToken` than `inputAmount_B` alone would produce.
4. Attacker B declares a correspondingly larger `outputToken` UTXO amount in their circuit proof; since the circuit only checks internal conservation of declared amounts (`circuits/MainEVMCircuit.circom:167-168`) and Hinkal's outer check only compares its own balance delta to the declared amount (`contracts/Hinkal.sol:134-146`), the inflated UTXO passes all checks — B has stolen A's stranded `d` worth of value.

### Citations

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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-93)
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
```

**File:** circuits/MainEVMCircuit.circom (L152-168)
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
```
