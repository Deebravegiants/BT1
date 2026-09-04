### Title
Unbounded router calldata in `ExternalActionSwap`/`LifiExternalAction` lets an attacker drain stranded token balance via the `approveUnlimited` allowance, crediting it to their own output UTXO - (File: contracts/external-actions/swaps/ExternalActionSwap.sol, contracts/external-actions/swaps/LifiExternalAction.sol)

### Summary
`LifiExternalAction.callRouter` never constrains how much `inputToken` the router actually consumes when it is an ERC20: the computed `inputAmount` (derived from `-deltaAmounts[0]`) is only used in the native-ETH branch, while for ERC20s the router is simply invoked with attacker-controlled `externalActionMetadata` against a `type(uint256).max` allowance set by `approveUnlimited`. Combined with a fee-accounting path in `ExternalActionSwap.swap` that can strand `outputToken` value in the action contract when `circomData.relay == address(0)`, an attacker can construct a transaction that pulls stray/stranded balance out of the action and has it counted entirely as their own swap output, breaking the invariant that tokens leaving the action equal `-deltaAmountChanges` Hinkal sent it for that transaction.

### Finding Description
The claimed invariant: `swappedAmount` (and thus the value in the resulting `utxoSet[0]`) that leaves the action == `-deltaAmounts[0]` (the input the attacker officially deposited into this action for this transaction, per Hinkal's `deltaAmountChanges`).

Trace:
- `Hinkal._externalTransact` (`contracts/Hinkal.sol:234-261`) transfers exactly `-deltaAmountChanges[i]` of each token into the external action address before calling `runAction`, then hands `deltaAmountChanges` to the action [1](#0-0) .
- `ExternalActionSwap.swap` computes `inputAmount = uint256(-deltaAmounts[0])` (adjusted for flat fee) and passes it to `callRouter` [2](#0-1) .
- `LifiExternalAction.callRouter` sets `approveUnlimited(inputToken, router)` (approve `type(uint256).max`) and then calls `router.call(externalActionMetadata)` for the ERC20 branch — `inputAmount` is **never used** to bound this call; only the native-coin branch uses it as `msg.value` [3](#0-2) .
- `externalActionMetadata` is fully attacker-controlled raw calldata (`circomData.externalActionData.externalActionMetadata`), so the attacker can encode any router instruction that pulls more of `inputToken` than the officially declared `inputAmount`, limited only by the action contract's actual token balance and the router's own logic — the unlimited allowance from `approveUnlimited` removes the allowance check as a limiting factor [4](#0-3) .
- `swappedAmount` is measured purely as `outputToken` balance delta across the router call [5](#0-4) , so any extra `inputToken` consumed beyond the declared `inputAmount` is silently converted into extra `outputToken` that flows into `amountToSendToHinkal` and the attacker's own `utxoSet[0]` [6](#0-5) .

A source of stray `inputToken`/`outputToken` balance in the action contract exists: when `circomData.relay == address(0)` but `feeStructure.flatFee`/`variableRate` are non-zero and `outputToken == feeStructure.feeToken`, `sendToRelay` is a no-op (it checks `relay != address(0)`) [7](#0-6) , yet `totalFee` still subtracts `relayFee` from `amountToSendToHinkal` [8](#0-7) . That fee amount is deducted from the user's output but never transferred anywhere, permanently stranding it as real token balance inside the action contract. There is no rescue/reconciliation function anywhere in `ExternalActionBaseV2` or `ExternalActionSwap` to recover this.

Once such stray balance exists (from this relay=0 fee-accounting gap, from rounding/partial fills by the router, or from any other prior transaction that under-consumed its declared `inputAmount`), any subsequent attacker transaction can craft `externalActionMetadata` that instructs the router to pull that stray balance too (via the unlimited allowance) as part of "their" swap, and the entire resulting output is credited to their own `stealthAddressStructure` UTXO. Existing guards do not catch this: `performHinkalChecks`, `verifyProof`, `insertNullifiers`, and the circuit's `inTotal + amountChanges === outTotal` constrain what the *proof* claims about the attacker's own UTXOs, but they have no visibility into how much of the action contract's on-chain token balance the router actually consumed — that is an on-chain balance-diff computation entirely decoupled from `deltaAmountChanges` for ERC20 inputs.

### Impact Explanation
An unprivileged attacker can capture stranded token value inside the `ExternalActionSwap`/`LifiExternalAction` contract as their own output UTXO, beyond what Hinkal recorded as `-deltaAmountChanges` for their transaction. This is direct theft of value that belongs to the protocol/other users (previously-stranded fee remainders or dust), matching Critical severity ("direct theft of shielded or in-flight user funds"). It is repeatable each time new stray balance accumulates (e.g., every relay-less swap with non-zero `flatFee`/`variableRate` on the fee token leaves a new residual that the next attacker can sweep).

### Likelihood Explanation
- Preconditions: (1) attacker must be an allowed caller into the swap flow through Hinkal (any depositor can do this — no privileged role needed); (2) some stray `inputToken`/`outputToken` balance must exist in the action contract, which the relay=`address(0)` fee-accounting gap reliably creates without needing any other bug, and which the attacker can also self-seed across two of their own transactions.
- Attacker cost: gas plus a small deposit to trigger the action; capital requirement to seed the residual is proportional to the fee rate, but stealing it back requires no extra capital beyond crafting calldata for the router.
- Feasibility: attacker fully controls `externalActionMetadata`, `deltaAmountChanges` (via a tiny genuine deposit), and can call the router with any calldata the router will accept, since `approveUnlimited` removes the allowance ceiling.
- Repeatable per residual event.

### Recommendation
1. Enforce that the ERC20 branch of `callRouter` actually consumes exactly `inputAmount` of `inputToken` — measure `inputToken` balance before/after the router call and `require` the decrease equals `inputAmount` (mirroring the output-side balance-diff check), instead of relying on unbounded router calldata plus unlimited approval.
2. Reset/limit the router approval to exactly `inputAmount` per call (`approveERC20Token`) rather than `approveUnlimited`, and revoke/reset it after the call.
3. Fix the relay-fee accounting gap: when `circomData.relay == address(0)`, do not subtract `relayFee`/`hinkalFee` from `amountToSendToHinkal` unless they are actually transferred, or require `relay != address(0)` whenever `flatFee`/`variableRate` are non-zero (mirroring the `_internalTransact` `"relay not paid"` check for the external-action path).
4. Add a reconciliation/rescue mechanism (privileged) to recover any pre-existing stray balance so it cannot be opportunistically claimed by the next unrelated caller.

### Proof of Concept
Foundry plan:
1. Deploy `LifiExternalAction` with a mock router and mock ERC20 tokens A (input) and B (output).
2. Seed a stray balance: perform a swap transaction with `circomData.relay == address(0)`, `feeStructure.flatFee > 0`, `feeStructure.feeToken == outputToken (B)`, and a mock router that returns a fixed amount of B. Assert `amountToSendToHinkal == swappedAmount - flatFee - hinkalFee` was sent to `msg.sender`, and separately assert `IERC20(B).balanceOf(action) == flatFee` (the stranded residual) — this is the left side of the broken equality (residual > 0 though `-deltaAmountChanges` for token B this tx was 0).
3. Second transaction, attacker deposits a small `inputAmount` of token A (e.g., 1 wei), but crafts `externalActionMetadata` for the mock router to also sweep the stray B balance already sitting in the action plus swap the fresh A into more B than a legitimate 1-wei swap should produce (mock router: on call, `transferFrom` amount encoded in calldata rather than tied to `inputAmount`).
4. Assert `swappedAmount` (and thus `utxoSet[0].amount`) received by the attacker's UTXO is strictly greater than what corresponds to `-deltaAmounts[0]` for that transaction, i.e. `utxoSet[0].amount != -deltaAmountChanges_hinkal_sent - fees`, proving the invariant break and that the stray/stranded balance became attacker-owned shielded value.

### Citations

**File:** contracts/Hinkal.sol (L244-260)
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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L70-101)
```text
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

**File:** contracts/Transferer.sol (L178-190)
```text
    function sendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) internal {
        if (relay != address(0) && actualAmount > 0) {
            transferERC20TokenOrETH(
                erc20TokenAddress,
                relay,
                uint256(actualAmount)
            );
        }
    }
```
