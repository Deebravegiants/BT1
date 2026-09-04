### Title
`Hinkal.transact`'s per-token balance-diff check double-counts a single real transfer across two `erc20TokenAddresses` entries when a proxy/aliasing token exposes the same underlying balance at two addresses, minting unbacked shielded and on-chain value - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.transact` snapshots and re-checks balances per-index over `circomData.erc20TokenAddresses` via `getBalancesForArray`, assuming each index observes an independent token balance. An attacker can supply an array containing the real token address plus a self-deployed "alias" contract whose `balanceOf`/`transferFrom` simply forward to the real token, so a single real transfer is observed as a balance increase at *two* indices. This lets the attacker satisfy the per-index equality `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` twice for one real deposit, minting an extra unbacked shielded UTXO/off-chain change denominated in the real token address.

### Finding Description
The broken equality: for a single real ERC20 transfer of `X` tokens into the vault, the protocol invariant should be `net real tokens received == sum(amountChanges) + sum(on-chain UTXO amounts)`. The vulnerable code allows `2X` of credited value (`X` as an off-chain `amountChanges` deposit + `X` as an on-chain UTXO) to be recorded against only `X` real tokens received.

Code path:
- `Hinkal.sol::transact` takes `oldBalances`/`newBalances` snapshots via `getBalancesForArray(circomData.erc20TokenAddresses)` [1](#0-0) , then iterates each index independently computing `balanceDif` and checking it against `amountChanges[i]`/`utxoAmount` with no cross-index correlation or uniqueness requirement on `erc20TokenAddresses` [2](#0-1) .
- `getBalancesForArray`/`getERC20OrETHBalance` in `Transferer.sol` simply call `IERC20(erc20TokenAddresses[i]).balanceOf(address(this))` per entry, with no check that different addresses correspond to independent balances [3](#0-2) .
- `DepositOnChainUtxosExternalAction.runAction` performs `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` per index and builds `utxoSet` entries whose `erc20Address` is simply `circomData.erc20TokenAddresses[i]` for that index, with no cross-check against other indices [4](#0-3) .
- `dimensionsCheck`/`checkOnchainCreation` in `HinkalHelper.sol` only validate array-length equality and that `amountChanges[i] == 0` when `onChainCreation[i]` is true; neither enforces that `erc20TokenAddresses` entries are distinct real tokens or independently-backed balances [5](#0-4) [6](#0-5) .

Attacker's exact call and exploit flow:
1. Attacker deploys "alias" contract `B` whose `balanceOf(who)` forwards to the real token `A`'s `balanceOf(who)`, and whose `transferFrom(from, to, amt)` forwards to `A.transferFrom(from, to, amt)` using an allowance the attacker grants `B` on the real token `A`. `B` is fully attacker-controlled and can be deployed for any real, already-listed ERC20 (`A`).
2. Attacker calls `Hinkal.transact` through an external action such as `DepositOnChainUtxosExternalAction`, with `circomData.erc20TokenAddresses = [A, B]`.
   - Index 0 (`A`, real token): `onChainCreation[0] = false`, `amountChanges[0] = X` (an "off-chain" deposit credited as a valid shielded output in the attacker's own proof), no UTXO minted at this index (`utxoAmount[0] = 0`).
   - Index 1 (`B`, alias): `onChainCreation[1] = true`, `amountChanges[1] = 0` (required by `checkOnchainCreation`), and the external action's `utxoAmounts[1] = [X]`, causing `DepositOnChainUtxosExternalAction` to actually call `B.transferFrom(attacker, Hinkal, X)`, which forwards to `A.transferFrom` and moves `X` real tokens of `A` into the vault.
3. Because `B.balanceOf` mirrors `A`'s real balance, `getBalancesForArray` observes the *same* `X` increase at both index 0 and index 1 within the same `transact` call (both snapshots are taken once before and once after the single transfer).
4. Both per-index checks pass: index 1: `balanceDif == 0 + X` (on-chain UTXO of `X` denominated in address `B`); index 0: `balanceDif == X + 0` (off-chain shielded UTXO of `X` denominated in address `A`, the real, shared token).
5. Result: the vault only received `X` real tokens of `A`, but the ledger now credits `2X` of shielded value, of which the `X` credited under the *real* token address `A` is fully fungible with all other users' real `A` deposits in the shared pool and can later be withdrawn as real `A` tokens via a normal `transact` withdrawal, draining other depositors.

Why existing guards fail: `verifyProof`/circuit constraints (`inTotal + amountChanges === outTotal`, `OverflowPreventer`, etc.) only enforce internal shielded merkle-tree arithmetic for the attacker's own new UTXOs; they have no visibility into on-chain ERC20 semantics or into whether two `erc20TokenAddresses` entries alias the same real balance. `performHinkalChecks`/`dimensionsCheck`/`checkOnchainCreation` validate array lengths and flag consistency only, not economic/token-identity uniqueness. `rootHashExists`, `insertNullifiers`, `nonReentrant`, and `onlyAllowedRecipient` are unrelated to this check and do not constrain it.

### Impact Explanation
The attacker mints shielded value in a real, shared token address without corresponding backing, directly matching "minting shielded value without backing (protocol insolvency)" - Critical severity. The unbacked `X` credited under the real token address `A` is redeemable later as real tokens against the shared vault pool, meaning other users' legitimately-deposited `A` tokens can be drained. This is repeatable per attacker-deployed alias token and per deposit, scaling linearly with the number of times the attacker repeats the flow (bounded only by gas and the amount they're willing to route through their alias contract).

### Likelihood Explanation
Preconditions are fully within attacker capability per the threat model: they can deploy arbitrary token/alias contracts, choose `erc20TokenAddresses` ordering/content, craft `CircomData`/`Dimensions`, and generate their own valid proof for their own new shielded UTXOs. No privileged role, hook, or victim cooperation is required for the base exploit (a hook is not strictly necessary; the double snapshot within a single `transact` call is sufficient). Cost is limited to deploying one small alias contract and normal gas/proof-generation costs, making this cheap and highly repeatable.

### Recommendation
Do not trust attacker-chosen `erc20TokenAddresses` to represent independent balances. Enforce strict uniqueness of `erc20TokenAddresses` entries within a single `transact` call (revert on duplicates, including semantic duplicates is hard to detect purely on-chain — but strict address-equality de-duplication removes the two-index-same-address case). More robustly, compute a single aggregate balance check per unique token address across the whole array (sum `amountChanges`/`utxoAmount` per unique address) rather than per raw index, so that even if two indices reference the same underlying value, the net real balance delta must match the sum of credits for that one real balance, not be creditable twice. Additionally, consider disallowing arbitrary externally supplied token addresses for on-chain UTXO creation unless the token is on an allow-list/registry with verified independent accounting.

### Proof of Concept
Foundry test plan:
1. Deploy a real `MockERC20 A`; mint attacker `2X`.
2. Deploy `AliasToken B` whose `balanceOf(addr)` returns `A.balanceOf(addr)` and whose `transferFrom(from,to,amt)` calls `A.transferFrom(from,to,amt)` (attacker approves `B` to spend `A` on their behalf).
3. Deploy `Hinkal`, `HinkalHelper`, register `DepositOnChainUtxosExternalAction` as an external action.
4. Attacker approves `B` for `A` allowance of `X`.
5. Build `CircomData` with `erc20TokenAddresses = [A, B]`, `onChainCreation = [false, true]`, `amountChanges = [X, 0]`, `slippageValues` at `0`, `externalActionData.externalActionMetadata` encoding `utxoAmounts = [[], [X]]`, plus a valid proof for a new shielded off-chain UTXO of value `X` under token `A` for index 0.
6. Call `Hinkal.transact(...)`.
7. Assert: `A.balanceOf(Hinkal) - balanceBefore == X` (only one real transfer occurred) while the emitted `NewCommitment` events / merkle leaves show `2X` total credited value (one off-chain leaf of `X` for token `A`, one on-chain leaf of `X` for token `B`, mapped to the same real balance). Assert vault's real backing (`X`) is strictly less than total credited shielded value (`2X`), proving insolvency.

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

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L55-82)
```text
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
