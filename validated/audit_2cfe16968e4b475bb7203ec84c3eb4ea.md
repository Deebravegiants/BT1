### Title
Unbounded, uncapped-amount swap residual sweep via `LifiExternalAction`/`ExternalActionSwap` unlimited router approval - (File: `contracts/external-actions/swaps/LifiExternalAction.sol`, `contracts/external-actions/swaps/ExternalActionSwap.sol`)

### Summary
`ExternalActionSwap.swap()` forwards exactly `inputAmount = -deltaAmounts[0]` (the ZK-proof-committed amount) to `callRouter`, but `LifiExternalAction.callRouter()` never actually constrains how much of the input token the router pulls. For ERC20 input tokens it calls `approveUnlimited(inputToken, router)` [1](#0-0)  and then executes attacker-supplied `externalActionMetadata` directly against the router with no check on the amount actually transferred out of the contract. Any input-token dust left behind by a prior swap (e.g. because a router route only partially consumes the approved/transferred amount) sits unaccounted for in the `ExternalActionSwap` contract, exactly like the `memoryData.shareOut - memoryData.shareOwed` residual in the Tapioca `sellCollateral()` bug. Because the router allowance is unlimited and the router calldata is entirely attacker-controlled, any subsequent caller can construct `externalActionMetadata` that instructs the router to pull more of the input token than their own declared `inputAmount` (up to the whole stranded balance), route it, and have the resulting `swappedAmount` (computed purely from output-token balance-diff) credited entirely to themselves as a new shielded UTXO.

### Finding Description
`swap()` computes the input amount from the proof-committed `deltaAmounts[0]` and calls `callRouter(inputToken, inputAmount, outputToken, externalActionMetadata)` [2](#0-1) . However `inputAmount` is a pass-through parameter that `LifiExternalAction.callRouter` never enforces for ERC20 tokens - it only bounds `msg.value` for native ETH: [3](#0-2) 

For ERC20 tokens, the contract grants the router an unlimited allowance and then executes whatever calldata was supplied in `circomData.externalActionData.externalActionMetadata` - a value that is fully attacker-chosen (it is only integrity-checked via `calldataHash` against the caller's own submitted `CircomData`, not constrained in content by the circuit) [4](#0-3) . The output-side accounting (`swappedAmount`) is derived solely from the output-token balance difference around the router call [5](#0-4) , and the entire resulting `amountToSendToHinkal` (after fees) is forwarded to `msg.sender` (the `Hinkal` contract) and packaged into a single UTXO attributed to the calling user's `stealthAddressStructure` [6](#0-5) .

This breaks the intended equality that a user's UTXO output should equal only the value produced from *that user's own* declared input. If the `ExternalActionSwap` contract ever holds a residual balance of an input token - which happens whenever a prior swap under-consumes the amount Hinkal transferred it (e.g. any route where the router doesn't spend 100% of the approved/transferred tokens, leaving dust or unspent allowance-backed balance) - that residual is never returned to the original depositor and never reflected in any of Hinkal's balance-diff equations (`Hinkal.sol` only checks the calling transaction's own `balanceDif`) [7](#0-6) . Because of the unlimited router approval and unconstrained metadata, any later unprivileged EOA can craft `externalActionMetadata` that pulls that stranded balance too, mint themselves extra shielded output value from it, and have it validated by Hinkal's balance/UTXO equality check since that check only verifies the *aggregate* balance movement of the current call matches the returned UTXO amount - it has no way to know that part of the swept input was not the caller's own.

### Impact Explanation
This is a theft vector: an unprivileged EOA can permanently appropriate value that belongs to the protocol/other users (stranded swap residuals) by directing the trusted router to pull more tokens than their own committed input amount, using the unlimited allowance already granted by `ExternalActionSwap`. This satisfies the "theft of shielded or in-flight user funds" / "unauthorised asset movement" criteria - the wallet-equivalent contract balance is moved by a call the depositing user never authorized.

### Likelihood Explanation
Requires (1) that `ExternalActionSwap`/`LifiExternalAction` at some point holds leftover input-token balance (plausible any time a router route does not consume the full approved amount, e.g. multi-hop/partial-fill routes, and there is no accounting or sweep-back logic for such dust), and (2) an attacker able to craft router calldata that pulls a larger amount than their declared `inputAmount` using the pre-existing unlimited allowance. Both preconditions are directly enabled by the current code (`approveUnlimited` + fully attacker-controlled `externalActionMetadata`), making this a design flaw rather than a purely theoretical one, though the exact amount stealable depends on how much residual has accumulated, which is a `router`-dependent externality outside this repo's direct control.

### Recommendation
- Enforce that the router only pulls up to `inputAmount` from `ExternalActionSwap`, e.g. by using a bounded/expiring approval (`approveToken(inputToken, router, inputAmount)` reset to `inputAmount` rather than `type(uint256).max`) instead of `approveUnlimited`, and by sweeping/returning any leftover input-token balance to `from`/`msg.sender` after the router call, mirroring the fixed Tapioca pattern of returning unspent proceeds instead of leaving them in the contract.
- After `callRouter`, compare input-token balance before/after the call and refund any residual (or fold it into the balance-diff equation) so `Hinkal.sol`'s balance-equality check accounts for all token movement, not only the output token.

### Proof of Concept
1. User A calls `Hinkal.transact` routing through `LifiExternalAction`, with `externalActionMetadata` describing a swap route (e.g., a multi-hop route via LI.FI) that only partially consumes the ERC20 `inputAmount` transferred to `ExternalActionSwap` by `Hinkal._externalTransact` [8](#0-7) , leaving unspent input-token balance in `ExternalActionSwap` (the router's unlimited allowance permits this without reverting, and there is no explicit check that 100% of `inputAmount` was consumed).
2. Attacker B (unprivileged EOA) generates their own valid Hinkal proof/`CircomData` for a small deposit of the same input token and crafts `externalActionMetadata` whose swap-route parameters specify pulling an amount larger than B's own declared `inputAmount` (up to the stranded balance + B's own funds), relying on `approveUnlimited` already granted to the router.
3. `callRouter` executes B's calldata; the router pulls the larger amount (including A's stranded residual) via the pre-existing unlimited allowance and returns a larger `outputToken` amount to `ExternalActionSwap`.
4. `swappedAmount` is computed purely from output-token balance diff [9](#0-8)  and the whole amount (minus fees) is credited to B's `stealthAddressStructure` as a new UTXO [10](#0-9) , while `Hinkal.sol`'s balance-diff check for B's transaction passes because it only checks that the aggregate output-token balance change equals the returned UTXO amount, with no knowledge that part of that value originated from A's stranded residual.

Note: I was unable to fully verify from the indexed code whether the LI.FI router itself would reject a `transferFrom` amount that exceeds what the accompanying route parameters expect internally (this depends on the external router's own logic, which is out of this repo's scope); the root-cause weakness identified here - unlimited allowance combined with unconstrained, attacker-supplied router calldata and no residual-sweep/refund logic - is confirmed directly in this repo's code.

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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-68)
```text
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
