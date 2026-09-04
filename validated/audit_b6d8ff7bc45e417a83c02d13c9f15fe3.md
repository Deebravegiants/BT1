### Title
Double-counting of `msg.value` when `address(0)` (ETH) is listed twice in `circomData.erc20TokenAddresses` mints shielded value without backing - ([File: contracts/Hinkal.sol])

### Summary
In `Hinkal.transact()`, the per-token balance-difference calculation re-adds `msg.value` for every array index whose `erc20TokenAddresses[i] == address(0)`, instead of adding it only once for the actual single ETH transfer. An attacker who lists `address(0)` twice (directly, and reusable as a second "ETH slot") can make the `balanceDif == amountChanges[i] + utxoAmount` check pass independently at both indices using the same, single `msg.value`, letting the circuit mint two UTXOs worth `msg.value` each while only one `msg.value` of ETH actually entered the contract.

### Finding Description
The broken equality is:

`net ETH entering Hinkal (msg.value, transferred once)` **≠** `sum_i amountChanges[i] for all i where erc20TokenAddresses[i] == address(0)` (2 × msg.value when address(0) appears twice with amountChanges[i] = msg.value each).

Code path in [1](#0-0) :

- `oldBalances`/`newBalances` are captured via `getBalancesForArray(circomData.erc20TokenAddresses)` [2](#0-1) , which for a payable call already includes `msg.value` in `address(this).balance` at both the "old" and "new" snapshot (since `_internalTransact`'s ETH path is only a `require(msg.value == _value)` check with no additional transfer when `_to == address(this)`, per `transferERC20TokenFromOrCheckETH` [3](#0-2) ).
- For each `i` where `erc20TokenAddresses[i] == address(0)`, the loop computes `balanceDif = newBalances[i] + msg.value - oldBalances[i]` [4](#0-3) . Since `newBalances[i] == oldBalances[i]` (no real second transfer occurred), this evaluates to `msg.value` for **every** occurrence of `address(0)` in the array, not just once for the actual single deposit.
- The equality check `balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount` [5](#0-4)  is then evaluated independently per index. With `amountChanges = [msg.value, msg.value]` and `onChainCreation = [false, false]`, both indices see `balanceDif = msg.value = amountChanges[i] + 0`, so both pass, even though only one `msg.value` was ever received by the contract.

Root cause: `balanceDif` recomputation for `address(0)` unconditionally re-adds `msg.value` per loop iteration rather than accounting for it once across the whole `erc20TokenAddresses` array, and there is no uniqueness/dedup check on `erc20TokenAddresses` (per the stated precondition, `dimensionsCheck` in `HinkalHelper.sol` only validates array lengths against `tokenNumber`).

Attacker's exact call: `transact(a, b, c, dimensions, circomData)` with `circomData.erc20TokenAddresses = [address(0), address(0)]`, `circomData.amountChanges = [msg.value, msg.value]`, `circomData.onChainCreation = [false, false]`, sending `msg.value` once, and a proof whose private witness creates two independent sets of output UTXOs (each crediting `msg.value` for token `address(0)`) at circuit indices 0 and 1. Because the circuit's per-index constraint `inTotal[i] + amountChanges[i] === outTotal[i]` (in `MainEVMCircuit.circom`) is evaluated per array slot and there's no constraint forcing `erc20TokenAddresses[i]` to be distinct, the prover can legally generate a valid proof that produces two UTXOs of `msg.value` each for the same underlying ETH.

Existing guards don't stop this: `performHinkalChecks`/`dimensionsCheck` only checks array-length consistency, not address uniqueness; `verifyProof` only checks the circuit constraints hold for the public inputs supplied (which include the duplicated address and amountChanges as ordinary public signals, not specially constrained); `rootHashExists`, `insertNullifiers`, and nullifier tracking address spend-once for *inputs*, not the outputs being over-minted; the on-chain `balanceDif` check is the only place meant to tie real asset movement to `amountChanges`, and it is exactly the mechanism broken here.

### Impact Explanation
The attacker mints shielded UTXOs worth `2 × msg.value` while only depositing `msg.value` of real ETH into the contract. This is uncollateralized minting of shielded value — a direct insolvency of the shielded pool that will be discovered later when other users' legitimate deposits are drained to honor withdrawal of the phantom extra UTXO. This matches the Critical category: "minting shielded value without backing." It is repeatable per transaction (each call with duplicated `address(0)` entries and one `msg.value` mints an extra `msg.value` of phantom shielded balance), and is fully attacker-controlled (no privileged role required — attacker only needs to craft `circomData` and generate a matching proof for their own UTXOs).

### Likelihood Explanation
Preconditions are trivial and entirely within an unprivileged attacker's control: choose `erc20TokenAddresses` with `address(0)` repeated, set matching `amountChanges`, and generate a valid proof for the desired UTXO outputs (attacker fully controls their own witness/private inputs). No special tree state, no interaction with other users, and no on-chain uniqueness enforcement blocks it as described. The only cost is a single real ETH deposit of `msg.value` and gas; the gain is doubling (or more, with more duplicate entries) the shielded credit for that one deposit. This is straightforward, cheap, and repeatable.

### Recommendation
Deduplicate ETH/native-token accounting: track the total real balance change for `address(0)` once across the whole `erc20TokenAddresses` array (e.g., compute the aggregate `address(this).balance` delta including `msg.value` exactly once, outside the per-index loop, and error out if `address(0)` appears more than once), or alternatively enforce uniqueness of `erc20TokenAddresses` entries in `dimensionsCheck`/`performHinkalChecks` so each token (including ETH) can only be referenced once per `transact()` call. The `balanceDif` formula for `address(0)` should not add `msg.value` per occurrence; it should be added exactly once to the sum of `balanceDif` across all indices mapping to `address(0)`.

### Proof of Concept
Hardhat test plan:
1. Deploy `Hinkal` with mocked verifier that accepts a crafted proof (or use test verifier bypass) so `verifyProof` returns true for a proof whose public inputs encode `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [msg.value, msg.value]`, `onChainCreation = [false, false]`, and two output commitments each representing a `msg.value` shielded UTXO for token `address(0)`.
2. Call `transact(...)` with `{ value: msg.value }` once.
3. Assert `address(hinkal).balance` increased by exactly `msg.value` (real ETH movement), i.e. `newContractBalance - oldContractBalance == msg.value`.
4. Assert the transaction succeeds (does not revert on the `balanceDif == amountChanges[i] + utxoAmount` require at both `i=0` and `i=1`), confirming `balanceDif` was computed as `msg.value` for both indices despite only one real transfer.
5. Assert `circomData.amountChanges[0] + circomData.amountChanges[1] == 2 * msg.value`, demonstrating the shielded-credit side of the ledger (`2*msg.value`) diverges from the actual asset side (`msg.value`).
6. Follow-up: redeem both resulting UTXOs (each `msg.value`) via subsequent `transact()` withdrawal calls and show `2*msg.value` ETH can be withdrawn from the contract for a single `msg.value` deposit, proving other depositors' funds are used to cover the shortfall.

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

**File:** contracts/Hinkal.sol (L97-147)
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
            }
```

**File:** contracts/Transferer.sol (L111-128)
```text
    function transferERC20TokenFromOrCheckETH(
        address _contractAddress,
        address _from,
        address _to,
        uint256 _value
    ) internal {
        if (_contractAddress == address(0)) {
            require(
                msg.value == _value,
                "msg.value doesn't match needed amount"
            );
            if (_to != address(this)) {
                transferETH(_to, _value);
            }
        } else {
            transferERC20TokenFrom(_contractAddress, _from, _to, _value);
        }
    }
```
