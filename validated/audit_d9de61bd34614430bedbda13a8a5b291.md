### Title
Duplicate `address(0)` entries in `erc20TokenAddresses` let the ETH balance delta back two independent `amountChanges` slots, minting unbacked shielded ETH — (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact` computes, per index `i`, `balanceDif[i] = newBalances[i] + msg.value - oldBalances[i]` whenever `erc20TokenAddresses[i] == address(0)`, and separately requires `balanceDif[i] == amountChanges[i] + utxoAmount[i]` for every index independently [1](#0-0) . Nothing in `dimensionsCheck`/`checkOnchainCreation` rejects duplicate token addresses in `erc20TokenAddresses`, so an attacker can list `address(0)` twice, causing the same real ETH delta to independently satisfy two separate `amountChanges` entries and mint twice the shielded ETH actually deposited.

### Finding Description
**Broken equality:** the protocol invariant should be `sum(amountChanges[i] for erc20TokenAddresses[i]==address(0)) == msg.value + net ETH balance change`, counted once. Instead, the contract enforces the per-index requirement `balanceDif[i] == amountChanges[i] + utxoAmount[i]` independently for every `i`, with no cross-index constraint linking indices that share the same token address [1](#0-0) .

Because Solidity credits `msg.value` to `address(this).balance` before the function body runs, both `oldBalances[i]` and `newBalances[i]` (captured via `getBalancesForArray`) already include `msg.value` [2](#0-1) . For a pure internal deposit with no other ETH movement, `newBalances[i] == oldBalances[i]`, so `balanceDif[i] = msg.value` for *every* index `i` where `erc20TokenAddresses[i] == address(0)`. If the attacker lists `address(0)` at two indices `i` and `i'`, both `balanceDif[i]` and `balanceDif[i']` independently equal the same real `msg.value = V`.

Since `_internalTransact` never populates `utxoSet` (it stays empty for internal, non-external-action transactions), `utxoAmount` is 0 at every index, so the balance-equation check reduces to `amountChanges[i] == V` and `amountChanges[i'] == V` — both individually satisfiable with the same real `V`. The attacker crafts a proof (self-generated, since they control all `CircomData` fields) with `dimensions.tokenNumber = 2`, `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [V, V]`, zero input nullifiers (pure deposit), and two output UTXOs each of value `V` for token `address(0)`. Because the circuit's `inTotal + amountChanges === outTotal` constraint (per the audit-scoped circuit invariant) is evaluated per index without any check that distinct indices don't reuse the same token address, the proof verifies for both indices independently: `0 + V = V` twice.

Root cause: neither `dimensionsCheck` nor `checkOnchainCreation` in `HinkalHelper.sol` reject duplicate entries in `circomData.erc20TokenAddresses` [3](#0-2) , and `performHinkalChecks` only validates array lengths and calldata hash integrity, not uniqueness of token addresses [4](#0-3) .

Result: the attacker deposits `V` real ETH once, but mints two output UTXOs of shielded value `V` each — `2V` of shielded ETH minted while the contract only holds `V` backing ETH.

### Impact Explanation
This is a direct unbacked minting of shielded value: the shielded pool's accounted ETH liabilities exceed the actual ETH held by the contract by exactly `V` per exploited transaction. This matches the "Critical: minting shielded value without backing (protocol insolvency)" category — repeatable per transaction, scalable by increasing the number of duplicated `address(0)` indices (`tokenNumber`) to multiply the unbacked mint per call, up to whatever `Dimensions`/circuit limits allow.

### Likelihood Explanation
Preconditions are minimal: the attacker only needs to be able to deposit their own ETH and self-generate a valid Groth16 proof for `MainEVMCircuit` (no special role required, satisfying the "unprivileged attacker" rule). They fully control `Dimensions.tokenNumber`, `erc20TokenAddresses`, `amountChanges`, `onChainCreation`, and output UTXO structure. No relayer, whitelisted role, or victim interaction is needed — the exploit is a single self-authored `transact` call with `circomData.relay == address(0)` and `originalSender == msg.sender`. This is fully repeatable and the attacker cost is only the real ETH they deposit once per call, receiving double the shielded credit.

### Recommendation
Enforce uniqueness of `erc20TokenAddresses` entries in `dimensionsCheck` (reject duplicate addresses within a single `CircomData`), or alternatively restructure the balance-equation loop in `Hinkal.transact` to add `msg.value` to the aggregate ETH balance delta exactly once across the whole array (e.g., track a boolean "ETH already credited" flag and only add `msg.value` on the first `address(0)` occurrence, requiring all subsequent `address(0)` occurrences to use the plain `newBalances[i] - oldBalances[i]` formula), then additionally require that the circuit's public inputs/`checkOnchainCreation` guarantee no duplicate token slots.

### Proof of Concept
Foundry/Hardhat test plan:
1. Deploy `Hinkal`, `HinkalHelper`, verifier, and generate a locally-proved `MainEVMCircuit` witness with:
   - `dimensions.tokenNumber = 2`
   - `circomData.erc20TokenAddresses = [address(0), address(0)]`
   - `circomData.amountChanges = [V, V]`, `onChainCreation = [false, false]`
   - `inputNullifiers` all zero (pure deposit, `inTotal = 0` for both indices)
   - two off-chain output commitments each encoding value `V` for `address(0)`.
2. Call `hinkal.transact{value: V}(a, b, c, dimensions, circomData)` from an unprivileged EOA.
3. Assert: `require` checks pass (`balanceDif[0] == V == amountChanges[0]`, `balanceDif[1] == V == amountChanges[1]`), proof verifies, transaction succeeds.
4. Assert the equality violation: sum of newly created shielded UTXO value for `address(0)` == `2 * V`, while `address(this).balance` only increased by `V`. I.e., `mintedShieldedETH (2V) > actualETHBalanceDelta (V)`. [1](#0-0) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/Hinkal.sol (L78-90)
```text
            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );
```

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

**File:** contracts/HinkalHelper.sol (L64-90)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );
```

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```
