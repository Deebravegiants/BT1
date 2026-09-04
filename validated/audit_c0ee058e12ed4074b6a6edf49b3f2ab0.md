### Title
Unspent LI.FI swap input becomes untracked, sweepable ERC20 balance with a standing router approval - ([File: contracts/external-actions/swaps/LifiExternalAction.sol], [File: contracts/external-actions/swaps/ExternalActionSwap.sol])

### Summary
`ExternalActionSwap.swap` pushes the full `-deltaAmounts[0]` (`inputAmount`) into the router call via `LifiExternalAction.callRouter`, but never verifies that the router actually consumed `inputAmount` of `inputToken`; it only measures the real balance increase of `outputToken` to size the single UTXO it returns. Because `callRouter` also grants the router a persistent unlimited `approveUnlimited` allowance, any input tokens an attacker's crafted `externalActionMetadata` chooses not to forward to the router stay as raw, untracked ERC20 balance on the `LifiExternalAction` contract and can be swept out in a later, self-funded ("free") `Hinkal.transact()` call.

### Finding Description
Broken equality: `tokens actually consumed by router == -deltaAmountChanges[0] pushed by Hinkal into LifiExternalAction`.

- `Hinkal._externalTransact` (`contracts/Hinkal.sol:244-256`) unconditionally transfers `uint256(-deltaAmountChanges[i])` of the input token from Hinkal to the action contract *before* `runAction` even executes: [1](#0-0) 
- `ExternalActionSwap.swap` sets `inputAmount = uint256(-deltaAmounts[0])` and calls `callRouter(inputToken, inputAmount, outputToken, externalActionMetadata)`, but the return value `swappedAmount` is only used to size a single output-side UTXO; there is no post-call check that `inputToken`'s balance on the action contract actually decreased by `inputAmount`: [2](#0-1) 
- `LifiExternalAction.callRouter` grants the router a persistent, unlimited approval (`approveUnlimited`) and then executes an entirely attacker-supplied calldata blob (`externalActionMetadata`) against the fixed `router` address, measuring only `outputToken`'s balance delta: [3](#0-2) 
- Back in `Hinkal.transact`, the per-token equality `balanceDif == amountChanges[i] + utxoAmount` (`contracts/Hinkal.sol:92-147`) is computed purely from Hinkal's own balance and the returned `utxoSet`. For the input-token index there is no UTXO at all, so the check trivially reduces to `balanceDif == amountChanges[0]`, which already held the instant Hinkal pushed the funds out — it is completely blind to whether the LifiExternalAction contract actually forwarded that amount to the router: [4](#0-3) 

Because of this, an attacker can, in transaction 1, submit a legitimate swap where `externalActionMetadata` only instructs the router to pull/swap a fraction `Y` of the pushed `inputAmount X`. Hinkal's ledger closes cleanly (its own balance dropped by `X`, matching `amountChanges[0] = -X`), and the attacker gets a normal output UTXO for `Y`'s swap result. The remainder `X - Y` of `inputToken` sits as raw ERC20 balance inside `LifiExternalAction`, already unlimited-approved to `router`.

In transaction 2 (any later `Hinkal.transact` call, potentially from a different, unrelated address, since nothing ties the stranded balance to a specific depositor), the attacker crafts a proof with `amountChanges[0] = 0` for that token slot (a trivially satisfiable, no-op input) so `deltaAmountChanges[0] = 0` and Hinkal pushes no new funds. The attacker's `externalActionMetadata` then instructs the same `router` (using its still-standing unlimited allowance) to pull the stranded `X - Y` balance directly from `LifiExternalAction` and swap it to `outputToken`. `swappedAmount` reflects this real balance increase, `swap()` forwards it to Hinkal, and a fully legitimate output UTXO is minted under the attacker's stealth address — backed by real tokens that were never nullified/debited from the shielded pool in this second transaction.

This breaks the intended invariant that every unit of value entering or leaving the shielded pool is matched by a nullifier or a UTXO; existing guards (`performHinkalChecks`, `verifyProof`, the per-index `balanceDif` equation, `insertNullifiers`) do not catch it because they only observe Hinkal's own balance and the action's self-reported `UTXO` set, neither of which is tied to whether the action contract fully consumed what it received.

### Impact Explanation
Critical — theft of shielded funds. Value that left the shielded pool in transaction 1 (correctly nullified/accounted for) is only partially converted; the remainder is later re-minted into a brand-new UTXO in transaction 2 without any corresponding nullifier, effectively creating shielded value without backing relative to that second transaction's own inputs. This is repeatable: any address can strand a fraction of every swap it performs and sweep it later, and can even sweep dust/stranded balances left by other users' legitimate but imperfectly-routed LI.FI swaps.

### Likelihood Explanation
Fully permissionless and requires only two ordinary `transact()` calls with attacker-crafted `externalActionMetadata` (a capability explicitly available to any user of the LI.FI action). No privileged role, relay, or victim cooperation is needed. The only precondition is that `LifiExternalAction` must have previously called `approveUnlimited` for the token/router pair (which happens on the very first swap of that token) and hold a nonzero stranded balance, both of which the attacker can trivially create themselves in a preceding transaction.

### Recommendation
After `callRouter` returns, assert that the action contract's `inputToken` balance decreased by exactly `inputAmount` (revert otherwise), or compute the actual amount consumed and refund/UTXO the unspent remainder back into the shielded pool for the original depositor. Additionally, avoid unlimited persistent approvals to the router — approve exactly `inputAmount` before the call and reset to zero afterward, or use a limited approval that cannot be exploited by later, unrelated transactions.

### Proof of Concept
Foundry test outline:
1. Deploy `Hinkal`, `LifiExternalAction` with a mock LI.FI router that: on call 1, accepts `transferFrom` of only `Y < X` tokens and mints `Y`-proportional output; on call 2, accepts a `transferFrom` pulling the residual `X - Y` (already approved) and mints corresponding output.
2. Tx1: attacker deposits `X` of `inputToken` via a valid Hinkal proof, `deltaAmountChanges[0] = -X`, `externalActionMetadata` crafted to only route `Y` to the mock router. Assert `Hinkal.transact` succeeds, `LifiExternalAction.balanceOf(inputToken) == X - Y` after the call.
3. Tx2: attacker submits a second valid proof with `amountChanges[0] = 0` (no deposit) for `inputToken`, and `externalActionMetadata` instructing the mock router to pull the residual `X - Y` from `LifiExternalAction` via the standing allowance, swap to `outputToken`.
4. Assert `Hinkal.transact` succeeds in tx2, a new UTXO is minted for the attacker's stealth address corresponding to the swap of `X - Y`, and no nullifier/input UTXO was consumed for `inputToken` in tx2 — demonstrating value creation without a matching shielded debit.

### Citations

**File:** contracts/Hinkal.sol (L97-146)
```text
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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-102)
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
