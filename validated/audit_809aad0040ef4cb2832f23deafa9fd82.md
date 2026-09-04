### Title
Unbounded router allowance + uncapped `swappedAmount` lets an attacker convert stranded/residual `inputToken` balance in `ExternalActionSwap` into their own shielded output UTXO - ([File: contracts/external-actions/swaps/ExternalActionSwap.sol])

### Summary
`ExternalActionSwap.swap` measures the LI.FI swap output purely as a before/after balance delta of `outputToken` around an attacker-crafted `router.call(externalActionMetadata)`, while `LifiExternalAction.callRouter` grants the router an **unlimited** allowance over the whole `inputToken` balance held by the contract, not just the current tx's `inputAmount`. Because the router calldata is 100% attacker-supplied, an attacker can make the router consume any stray/residual `inputToken` balance sitting in the action (from a prior swap's un-swept refund, or simply self-seeded via a plain `ERC20.transfer`) together with their own tiny deposit, and walk away with a UTXO worth far more than `-deltaAmountChanges` Hinkal actually sent the action that transaction.

### Finding Description
Invariant claimed: `tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx`.

In `_externalTransact`, Hinkal only forwards `uint256(-deltaAmountChanges[i])` of `inputToken` to the action before calling `runAction`: [1](#0-0) 

Inside `ExternalActionSwap.swap`, `inputAmount` is derived from `deltaAmounts[0]` (the very amount Hinkal just sent), and is passed to `callRouter`, but the actual EVM calldata sent to the router (`circomData.externalActionData.externalActionMetadata`) is fully attacker controlled and opaque to the contract: [2](#0-1) 

`LifiExternalAction.callRouter` grants the router an *unlimited* allowance (`approveUnlimited`, up to `type(uint256).max`) over the contract's entire `inputToken` balance — not scoped to `inputAmount` — and then measures `swappedAmount` as a raw `outputToken` balance delta around the call, with no check that only `inputAmount` of `inputToken` was actually consumed: [3](#0-2) 

`approveUnlimited` confirms the allowance is not amount-bound: [4](#0-3) 

`swap()` also never checks or sweeps any leftover `inputToken` balance after the router call — it only forwards `outputToken` to Hinkal and mints a UTXO for the caller, with the caller's own `stealthAddressStructure`: [5](#0-4) 

This means: (1) any un-consumed/refunded `inputToken` from a prior legitimate swap that the LI.FI router refunds back into the action contract (instead of consuming it entirely) is permanently stranded there, since `swap()` never sweeps input-token residue back to the depositor or Hinkal; and (2) since the router's allowance is unlimited and its calldata is attacker-controlled, a subsequent attacker using the same `inputToken` can craft `externalActionMetadata` to have the router pull that stranded residue *plus* their own small deposit, producing an inflated `swappedAmount` that has no relationship to `-deltaAmounts[0]`.

Downstream, `Hinkal.sol`'s balance-diff check is tautological with respect to this: `utxoAmount` is derived directly from the `utxoSet` returned by the action (which reflects the inflated `swappedAmount`), so `balanceDif == amountChanges[i] + utxoAmount` always holds by construction and cannot detect the inflation: [6](#0-5) 

The ZK circuit constraint `inTotal + amountChanges[i] === outTotal` only binds the attacker's own proven leaves/nullifiers for their own transaction — it has no visibility into, or ability to constrain, what the router actually does with contract-held token balances during `callRouter`'s external call: [7](#0-6) 

Slippage checks are floors (`slippageValues[1] != 0`, `balanceDif >= slippageValues[i]`), not ceilings, so they don't stop excess output from being captured.

### Impact Explanation
An unprivileged attacker can extract any residual/stranded balance of `inputToken` sitting in the `ExternalActionSwap`/`LifiExternalAction` contract and redirect it, via the unlimited router allowance and attacker-crafted calldata, into their own shielded output UTXO — while only having funded a minimal `-deltaAmountChanges` themselves that transaction. This is direct theft of value that does not belong to the current transaction's proven input/output accounting (Critical: direct theft of shielded or in-flight user/protocol funds). It is fully repeatable each time residual balance accumulates in the contract, and the attacker does not even need to wait for organic residue — they can self-seed the stray balance with a plain `ERC20.transfer` to the action contract and immediately "launder" it into a shielded UTXO backed by a trivial proof/deposit.

### Likelihood Explanation
Preconditions are trivial and fully attacker-controllable: any residual `inputToken` balance in the action contract (which the attacker can create themselves via a direct token transfer, no protocol bug required), the ability to construct `externalActionMetadata` bytes for the LI.FI router specifying a pull amount larger than their own committed `inputAmount` (ordinary off-chain calldata construction, well within an unprivileged attacker's capability), and a normal Hinkal proof for a minimal deposit. No privileged role, relay, or victim cooperation is required, and the exploit is repeatable at will.

### Recommendation
Bind the router's token pull strictly to the current transaction's committed `inputAmount`:
- Replace `approveUnlimited` in `LifiExternalAction.callRouter` with an exact, single-use approval of `inputAmount` (reset to 0 before/after), so the router cannot pull more than what Hinkal actually funded this transaction.
- Additionally snapshot the `inputToken` balance before/after the router call and require the amount consumed equals exactly `inputAmount` (no under/over-consumption), reverting otherwise.
- Sweep any unavoidable leftover `inputToken` refunded by the router back to Hinkal/the depositor within the same transaction instead of leaving it stranded in the action contract indefinitely.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `LifiExternalAction` (with a mock LI.FI router), and a mock ERC20 `inputToken`/`outputToken` (test with 6-decimal `inputToken`).
2. Seed residue: directly `inputToken.transfer(address(lifiAction), residualAmount)` from a test account (simulating stranded refund or attacker self-seed).
3. Attacker performs a normal Hinkal `transact` call to `LifiExternalAction.runAction` with a minimal `deltaAmounts[0] = -tinyAmount`, and crafts `externalActionMetadata` for the mock router to pull `tinyAmount + residualAmount` of `inputToken` (allowed since `approveUnlimited` grants max allowance) and return a proportional `outputToken` amount.
4. Assert: `swappedAmount` returned by `callRouter` reflects consumption of `tinyAmount + residualAmount`, not just `tinyAmount`.
5. Assert broken equality: attacker's resulting UTXO amount (`amountToSendToHinkal`) `> f(-deltaAmountChanges[0])` alone — i.e., strictly greater than what the tiny funded delta alone could produce, proving residual value was captured beyond `-deltaAmountChanges` Hinkal sent that transaction.
6. Assert `inputToken.balanceOf(lifiAction)` post-tx no longer contains `residualAmount` (it was drained into attacker's UTXO), confirming theft of the parked balance.

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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L89-102)
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

**File:** circuits/MainEVMCircuit.circom (L167-169)
```text
      // for each token type, the sum of refund and swapped amount should be equal to the sum of input amounts
      inTotal + amountChanges[i] === outTotal;
	}
```
