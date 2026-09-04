Based on my analysis of `contracts/Hinkal.sol`, the vulnerability described in the question is valid.

### Title
Duplicate `erc20TokenAddresses` entries let a single physical UTXO be matched twice, inserting duplicate Merkle leaves for one real transfer - ([File: contracts/Hinkal.sol])

### Summary
In `Hinkal.transact`, the outer loop over `circomData.erc20TokenAddresses` re-scans the entire `utxoSet` array on every iteration for matching `erc20Address`. If the attacker duplicates the same token address at two indices, the single UTXO produced by an external action (e.g. `DepositOnChainUtxosExternalAction`) is matched and copied into `onChainCommitments` twice, and both per-index balance checks pass because they compare against the same aggregate token balance change.

### Finding Description
The broken equality: leaves inserted into the Merkle tree via `insertCommitments` should equal the number of value-bearing UTXOs whose amount was counted once in the balance/slippage equation. This is violated when `circomData.erc20TokenAddresses = [T, T]`.

Code path in `contracts/Hinkal.sol` `transact`: [1](#0-0) 

For a duplicated token T with one physical UTXO of amount `A` created on-chain (`onChainCreation[i]=true`, `amountChanges[i]=0` enforced by `checkOnchainCreation` in `contracts/HinkalHelper.sol`): [2](#0-1) 

- `getBalancesForArray(circomData.erc20TokenAddresses)` queries the balance of T twice (once per duplicated index), so `oldBalances[0]==oldBalances[1]` and `newBalances[0]==newBalances[1]`; the aggregate balance change `D=A` is identical at both indices.
- At i=0, the inner `j` loop scans `utxoSet` and matches the single UTXO entry, giving `utxoAmount=A`; balance check `D == 0 + A` passes; `onChainCommitments[0]` is built from that UTXO; counter=1.
- At i=1 (same token T), the inner `j` loop scans the *same* `utxoSet` array fresh and matches the *same* UTXO entry again, again giving `utxoAmount=A`; balance check `D == 0 + A` passes again; `onChainCommitments[1]` is built from the identical UTXO struct; counter=2.

Neither `dimensionsCheck` nor `checkOnchainCreation` (in `contracts/HinkalHelper.sol`) constrain that `erc20TokenAddresses` entries be unique, nor do they tie the number of `onChainCreation=true` slots to the number of physical UTXOs returned by the external action — they only check array-length consistency and that `amountChanges[i]==0`/`inputNullifiers[i]` are zeroed for on-chain-creation slots. `DepositOnChainUtxosExternalAction.runAction` iterates per-index and only requires that `deltaAmounts[i]==0` and `utxoAmounts[i].length` matches, which allows one index's `utxoAmounts[i]` to be empty (no additional transfer) while both indices reference the same token address T; only one real `transferERC20TokenFrom` for `A` occurs. [3](#0-2) 

`insertCommitments` then inserts both `onChainCommitments` entries as separate leaves (`hash4(A,T,stealth,ts)` twice) even though the contract only received `A` once.

### Impact Explanation
This mints shielded value without backing: the two identical leaves are each independently spendable by whoever holds the stealth key, allowing withdrawal of `2A` for a genuine deposit of `A`, directly causing protocol insolvency. This matches the Critical impact category ("minting shielded value without backing").

### Likelihood Explanation
The attacker needs only to be an ordinary depositor: craft `circomData.erc20TokenAddresses` with a duplicated token address, structure `externalActionData.externalActionMetadata` for `DepositOnChainUtxosExternalAction` so only one of the duplicated indices carries a non-empty `utxoAmounts[i]`, set the other duplicated index's `onChainCreation=true`/`amountChanges=0`, and generate a valid circuit proof for these self-chosen fields (the circuit's `inTotal + amountChanges === outTotal` constraint operates on per-index public inputs and does not itself dedupe token addresses or count physical UTXOs, since `onChainCommitments` are constructed on the Solidity side, not proven by the circuit). No privileged role or third party is required, and the attack is repeatable.

### Recommendation
Either (a) require `circomData.erc20TokenAddresses` to be strictly unique/sorted in `dimensionsCheck`, or (b) restructure the matching loop so each `utxoSet[j]` entry is consumed only once (e.g., track a "matched" flag per `j`, or remove matched entries from consideration in subsequent `i` iterations) so a single UTXO can never be counted, or turned into a commitment, more than once.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, register `DepositOnChainUtxosExternalAction` for a test ERC20 token `T`.
2. Build `circomData` with `erc20TokenAddresses = [T, T]`, `onChainCreation = [true, true]`, `amountChanges = [0, 0]`, `externalActionData.externalActionMetadata = abi.encode([[A],[]])` (one UTXO of amount `A` only at index 0), matching `inputNullifiers` zeroed and `slippageValues` set to allow `D=A`.
3. Generate a valid proof locally for this `circomData`/`dimensions` (assert `verifyProof` succeeds).
4. Call `Hinkal.transact` and assert:
   - Token `T` balance of `Hinkal` increased by exactly `A` (one physical transfer).
   - `insertCommitments` inserted **two** leaves equal to `hash4(A, T, stealthAddressStructure, timeStamp)` (query tree events/state for leaf count and values).
5. Perform two subsequent spend `transact` calls, each nullifying one of the two identical leaves and withdrawing `A`; assert total withdrawn `= 2A > 1A` deposited, demonstrating insolvency.

### Citations

**File:** contracts/Hinkal.sol (L92-132)
```text
            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
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
```

**File:** contracts/HinkalHelper.sol (L173-202)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-83)
```text
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );

            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
        }
```
