### Title
Native asset `msg.value` re-added per duplicate `address(0)` entry in `erc20TokenAddresses`, allowing shielded credit for value never physically deposited - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.transact`'s post-action balance reconciliation loop computes, for every index `i` where `circomData.erc20TokenAddresses[i] == address(0)`, `balanceDif = newBalances[i] + msg.value - oldBalances[i]`. Because this formula unconditionally re-adds the full `msg.value` at **every** occurrence of `address(0)` in the caller-supplied array rather than only once, an attacker who lists the native asset more than once (e.g. alongside the wrapped output token from a LI.FI swap external action) can make the per-index equality `balanceDif == amountChanges[i] + utxoAmount` hold at multiple independent indices for the same single, physical `msg.value` transfer.

### Finding Description
The invariant the protocol needs is: *real ETH/token that entered the vault in this call == sum of `amountChanges` credited off-chain + sum of on-chain UTXO amounts minted*. In `Hinkal.transact`: [1](#0-0) 

the reconciliation is done **per index `i`** of `circomData.erc20TokenAddresses`, not per unique token. Each call reads the same underlying balance (`getERC20OrETHBalance(address(0)) == address(this).balance`) for every occurrence of `address(0)` in the array: [2](#0-1) 

For `address(0)` entries, `balanceDif = newBalances[i] + msg.value - oldBalances[i]` (Hinkal.sol lines 100-104). `msg.value` is already reflected in `address(this).balance` at function entry (Solidity credits `msg.value` before the function body executes), so this formula is designed to "add back" `msg.value` exactly once, to compensate for ETH that is subsequently forwarded out to the external action as swap input. However, the addition of `msg.value` is keyed only on the *token address* being `address(0)`, not on whether this is the single, correct slot representing the actual native deposit. If `circomData.erc20TokenAddresses` contains `address(0)` at more than one index (e.g. `[address(0), WETH, address(0)]`, submitted alongside a LI.FI-swap `externalActionData` that only consumes indices `0` and `1`): [3](#0-2) 

then at *every* such duplicate index, the same physical `newBalances[i]-oldBalances[i]` delta gets `msg.value` re-added independently, producing the **same** `balanceDif` value `D` at each duplicate index. The attacker can then choose `circomData.amountChanges[i]` (or an on-chain UTXO amount) equal to `D` at each duplicate index, so that the equality `balanceDif == amountChanges[i] + utxoAmount` is satisfied multiple times from one real transfer of `msg.value`. This lets the corresponding shielded/on-chain credit be minted more than once for a single unit of real backing.

`_externalTransact`'s pre-action loop also iterates blindly over the full array (not just the swap's used indices 0/1): [4](#0-3) 

so extra duplicate-token slots are not rejected before reaching the balance-check; whether they are rejected by `dimensionsCheck`/`performHinkalChecks` in `HinkalHelper.sol` or by circuit-level uniqueness constraints in `MainEVMCircuit.circom` could not be fully confirmed with the tools available in this session — this is the main residual uncertainty for this finding.

### Impact Explanation
If duplicate-token array entries are not rejected upstream, the attacker can cause `amountChanges`/on-chain UTXO credit to be issued multiple times against a single native-asset transfer, i.e. **minting shielded value without backing funds** — matching the Critical impact category (protocol insolvency, direct value creation from nothing). The attack is repeatable per transaction and costs only the gas plus one real `msg.value` deposit.

### Likelihood Explanation
Preconditions: the attacker must be able to submit `circomData.erc20TokenAddresses` with `address(0)` appearing more than once, paired with a valid proof whose public inputs are consistent with the (attacker-chosen) `amountChanges` array for each index, and the `externalActionId` must be a swap action (or `0`) that doesn't itself enforce array-length/uniqueness of exactly two entries. This is fully achievable by an unprivileged EOA since they control `erc20TokenAddresses`, `amountChanges`, and generate their own proof — **unless** `dimensionsCheck` in `HinkalHelper.sol` or a circuit constraint enforces a fixed/unique token-slot layout, which could not be verified within this investigation's scope and tool budget. Given this uncertainty, likelihood should be treated as conditional on that verification.

### Recommendation
- Deduplicate `circomData.erc20TokenAddresses` before/within `Hinkal.transact`, rejecting any array containing the same address (including `address(0)`) more than once.
- Alternatively, restructure the native-asset accounting so `msg.value` is added to the balance-delta calculation exactly once per transaction (e.g. track a `bool nativeAccountedFor` flag across the loop) rather than once per matching array index.
- Enforce in `dimensionsCheck`/circuit constraints that `erc20TokenAddresses` entries are unique and match exactly the token slots the selected `externalActionId` is designed to use (e.g. exactly 2 entries, input/output, for swap actions).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `LifiExternalAction` (with a mock router), a mock WETH token, and register the external action.
2. Build `circomData` with `erc20TokenAddresses = [address(0), WETH, address(0)]`, `amountChanges = [-inputAmount, +expectedOut, +inputAmount]` (duplicate positive credit at index 2 for the same `msg.value` used at index 0), `onChainCreation` all `false`, valid `slippageValues`, and a locally generated proof consistent with these public inputs (assuming circuit does not reject duplicate token slots).
3. Call `transact{value: inputAmount}(...)`.
4. Assert: actual vault ETH balance change (`address(hinkal).balance` before vs after, net of the router mock consuming `inputAmount`) is less than the sum of shielded credits implied by `amountChanges[0] + amountChanges[2]`.
5. Assert both per-index checks at Hinkal.sol lines 137-146 pass with the same `balanceDif` value `D`, while `sum(real inflow) != amountChanges[0] + amountChanges[2] + utxoAmount`, demonstrating the broken invariant `net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts)`.

Note: full confirmation requires inspecting `HinkalHelper.performHinkalChecks`/`dimensionsCheck` (not reviewed in this session) to confirm it does not already reject duplicate `erc20TokenAddresses` entries; if it does, this exploit path is blocked upstream.

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

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

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

**File:** contracts/Transferer.sol (L149-176)
```text
    function getERC20OrETHBalance(
        address _erc20TokenAddress
    ) internal view returns (uint256) {
        if (_erc20TokenAddress == address(0)) {
            return address(this).balance;
        } else {
            IERC20 outToken = IERC20(_erc20TokenAddress);
            return outToken.balanceOf(address(this));
        }
    }

    function getBalancesForArrayMemory(
        address[] memory erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }

    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
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
