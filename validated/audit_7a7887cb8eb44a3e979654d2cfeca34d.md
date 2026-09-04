### Title
Missing slippage-floor enforcement in `ExternalActionSwap.swap()` enables MEV sandwich theft of user swap output - (File: contracts/external-actions/swaps/ExternalActionSwap.sol)

### Summary
`ExternalActionSwap.sol` only checks that a slippage-floor value is *non-zero*, but never actually compares the real swap output against that floor. Any unprivileged actor can sandwich the underlying router call (e.g. via `LifiExternalAction`) and the contract will still accept and shield whatever (possibly drastically reduced) output amount comes back, silently breaking the value guarantee the user signed for.

### Finding Description
`swap()` in `ExternalActionSwap.sol` requires `circomData.slippageValues[1] != 0` as its only slippage-related check: [1](#0-0) 

The user-signed `slippageValues[1]` is meant to represent a minimum acceptable output ("floor"), analogous to `amountOutMin` in the external report. However, after `callRouter` returns `swappedAmount`, there is no comparison such as `require(swappedAmount >= uint256(circomData.slippageValues[1]))`: [2](#0-1) 

The concrete implementation, `LifiExternalAction.callRouter`, simply forwards attacker/relay-suppliable `externalActionMetadata` to the router and measures the balance delta as `swappedAmount` — with no independent floor check performed by the contract itself: [3](#0-2) 

Because the on-chain contract never enforces the user-signed floor, whatever `swappedAmount` the router returns — even if depressed by a front-run/back-run sandwich — is accepted, fee-deducted, and shielded into the resulting UTXO: [4](#0-3) 

This is the same root-cause bug class as the external report (zero/ineffective `amountOutMin`), except here the affected code (`ExternalActionSwap.sol`/`LifiExternalAction.sol`) is part of the live, non-deprecated contract set in this repo, so the "Not Applicable — deprecated" remediation does not apply.

### Impact Explanation
The `slippageValues[1]` field is a user-signed protection parameter but is effectively ignored by the contract logic, so an unprivileged mempool observer can sandwich the swap transaction and extract the difference between the fair-market output and the manipulated output — this is direct theft of in-flight shielded user funds during the external swap action, satisfying the Critical impact bar ("direct theft of shielded or in-flight user funds").

### Likelihood Explanation
Any external, unprivileged party monitoring the public mempool can execute a standard front-run/back-run sandwich against the router call triggered by `runAction`/`swap`; no admin, relay, or signer key is required, and the "protection" the user relies on (`slippageValues[1] != 0`) provides no actual on-chain enforcement, making exploitation straightforward and repeatable for every swap external action.

### Recommendation
- In `ExternalActionSwap.swap()`, after computing `swappedAmount`, add `require(swappedAmount >= uint256(circomData.slippageValues[1]), "swap output below floor");` so the user-signed floor is actually enforced rather than merely checked for non-zero.
- Ensure `slippageValues` is bound into the same signed/public-input commitment used elsewhere (e.g. alongside `calldataHash`) so a relay cannot alter it independently of the rest of the transaction.

### Proof of Concept
1. User signs a swap external action with `slippageValues[1] = X` (intended minimum output) and submits it through the relay/mempool.
2. Attacker observes the pending transaction, front-runs it by buying the output token to move price against the user, then lets the `LifiExternalAction.callRouter` execute at the worse price.
3. `swappedAmount` returned is far below `X`, but since `ExternalActionSwap.swap()` never checks `swappedAmount` against `slippageValues[1]` (only checks `slippageValues[1] != 0`), the transaction proceeds normally: fees are deducted and the reduced `amountToSendToHinkal` is shielded into a new UTXO.
4. Attacker back-runs, selling the output token back at the inflated price, pocketing the value the user lost — with no revert and no on-chain trace that the floor was violated.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L51-61)
```text
        address outputToken = circomData.erc20TokenAddresses[1];

        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-102)
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
