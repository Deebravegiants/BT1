### Title
Duplicate `address(0)` entries in `erc20TokenAddresses` let a single `msg.value` back two independent `amountChanges` credits, minting unbacked shielded ETH - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact` iterates `circomData.erc20TokenAddresses` and, for every index whose token is `address(0)`, adds `msg.value` on top of the balance delta before checking it against `amountChanges[i]` [1](#0-0) . Nothing in `dimensionsCheck` or elsewhere rejects duplicate token addresses in that array [2](#0-1) , so an attacker can list `address(0)` twice and have `msg.value` counted once per occurrence, satisfying two independent `amountChanges` credits with a single ETH payment.

### Finding Description
The claimed equality is: **real ETH received (`msg.value`) == sum of `amountChanges` credited across all `address(0)` slots in the batch.** With duplicate entries this equality is broken: 2×`msg.value` worth of `amountChanges` is credited for 1×`msg.value` actually paid.

Trace:
1. `oldBalances`/`newBalances` are captured via `getBalancesForArray(circomData.erc20TokenAddresses)` once per index in the array [3](#0-2) . `msg.value` is already credited to `address(this).balance` before the function body runs (payable call semantics), so it is present in both snapshots and cancels out for ETH unless deliberately re-added.
2. For each index `i` where `erc20TokenAddresses[i] == address(0)`, the code explicitly re-adds `msg.value`: `balanceDif = newBalances[i] + msg.value - oldBalances[i]` [4](#0-3) .
3. If the attacker puts `address(0)` at two indices `i` and `k` (with dimensions/tokenNumber sized accordingly — no uniqueness check exists in `dimensionsCheck`), both indices reference the *same* underlying ETH balance, so `newBalances[i]==newBalances[k]` and `oldBalances[i]==oldBalances[k]`. Both `balanceDif[i]` and `balanceDif[k]` independently equal `(actual net ETH movement) + msg.value`.
4. The per-index balance equation `require(balanceDif == amountChanges[i] + utxoAmount)` [5](#0-4)  is checked **independently** for each index — there is no cross-index constraint tying together the two `address(0)` slots. The attacker can therefore set `amountChanges[i] = msg.value` and `amountChanges[k] = msg.value` (with net ETH movement = 0), and both requires pass.
5. In `_internalTransact`, each positive `deltaAmountChange` triggers `transferERC20TokenFromOrCheckETH(address(0), externalAddress, address(this), amountChanges[i])`, which for ETH only asserts `msg.value == _value` (no actual pull, since `_to == address(this)`) [6](#0-5) . Since both slots claim the same numeric value `msg.value`, this check trivially passes twice — no second payment is ever demanded.
6. The circuit-side constraints (`inTotal + amountChanges === outTotal`, `OverflowPreventer`, etc.) operate per public-input token slot and do not enforce uniqueness of `erc20TokenAddresses`; the prover is free to emit two ETH slots each with `amountChanges = msg.value`, and each slot's own in/out totals balance internally.

Net effect: one `msg.value` payment backs two independent `amountChanges` credits, so the resulting shielded UTXOs (or on-chain amount changes) sum to `2 × msg.value` while only `1 × msg.value` of ETH entered the contract — unbacked shielded value is minted.

The `prooflessDeposit` path is not vulnerable to this exact issue: `_calcTokenChangesForProoflessDeposit` deduplicates repeated addresses by summing amounts into a single unique-token entry before transfers occur [7](#0-6) , and `_handleTransfersFromProoflessDeposit` strictly checks `balanceAfter - balanceBefore == amount` per unique token [8](#0-7) . The real vulnerable entrypoint is `Hinkal.transact`, not `prooflessDeposit`.

### Impact Explanation
An attacker deposits `msg.value` once but obtains shielded/on-chain ETH commitments worth `2 × msg.value` (or more, with additional duplicate `address(0)` slots), directly minting unbacked shielded value and causing protocol insolvency — this is a Critical impact matching "minting shielded value without backing." It is fully repeatable by any unprivileged depositor for arbitrary amounts and array-length duplication counts, limited only by `dimensions.tokenNumber`/array-size constraints, not requiring any privileged role.

### Likelihood Explanation
The attacker needs only to: build a valid `CircomData`/proof for a normal `transact` call with `externalActionData.externalActionId == 0` (internal deposit), list `address(0)` at two (or more) indices in `erc20TokenAddresses`, set matching `amountChanges[i] = amountChanges[k] = msg.value`, and set `slippageValues`/`onChainCreation` consistently. No relay, no admin role, and no compromised dependency is required — the attacker generates the proof themselves for their own UTXOs. This is a low-cost, fully attacker-controlled and repeatable exploit.

### Recommendation
Enforce uniqueness of `erc20TokenAddresses` (or at minimum of `address(0)` occurrences) in `dimensionsCheck`/`performHinkalChecks`, or compute the `msg.value` adjustment once globally (outside the per-index loop) rather than re-adding it for every index that happens to equal `address(0)`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, verifier mocks/stub that accept a crafted proof (or use the repo's existing test harness to build a `CircomData` with `dimensions.tokenNumber = 2`).
2. Build `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [X, X]`, `onChainCreation = [false, false]`, `slippageValues = [X, X]`, `externalActionData.externalActionId = 0`, `externalActionData.externalAddress = attacker`.
3. Call `hinkal.transact{value: X}(a, b, c, dimensions, circomData)`.
4. Assert both balance-equation `require`s at [5](#0-4)  pass with only `X` wei sent (`address(this).balance` increases by exactly `X`, not `2X`).
5. Assert the two inserted commitments/UTXOs together represent `2X` of shielded ETH value (via `insertCommitments`/emitted `OnChainCommitment`/off-chain UTXO amounts), demonstrating `sum(minted ETH UTXO value) == 2X > address(this).balance delta == X`.

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

**File:** contracts/Hinkal.sol (L97-114)
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
```

**File:** contracts/Hinkal.sol (L137-146)
```text
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

**File:** contracts/Hinkal.sol (L297-324)
```text
    function _calcTokenChangesForProoflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts
    )
        private
        pure
        returns (TokenWithAmount[] memory uniqueTokens, uint256 uniqueCount)
    {
        uniqueTokens = new TokenWithAmount[](erc20Addresses.length);

        for (uint256 i = 0; i < erc20Addresses.length; i++) {
            bool found = false;
            for (uint256 j = 0; j < uniqueCount; j++) {
                if (uniqueTokens[j].erc20Address == erc20Addresses[i]) {
                    uniqueTokens[j].amount += amounts[i];
                    found = true;
                    break;
                }
            }
            if (!found) {
                uniqueTokens[uniqueCount] = TokenWithAmount({
                    erc20Address: erc20Addresses[i],
                    amount: amounts[i]
                });
                uniqueCount++;
            }
        }
    }
```

**File:** contracts/Hinkal.sol (L356-381)
```text
    function _handleTransfersFromProoflessDeposit(
        TokenWithAmount[] memory uniqueTokens,
        uint256 uniqueCount
    ) private {
        for (uint256 i = 0; i < uniqueCount; i++) {
            address erc20Address = uniqueTokens[i].erc20Address;
            uint256 amount = uniqueTokens[i].amount;

            uint256 balanceBefore = getERC20OrETHBalance(erc20Address);
            if (erc20Address == address(0)) balanceBefore -= msg.value;

            transferERC20TokenFromOrCheckETH(
                erc20Address,
                msg.sender,
                address(this),
                amount
            );

            uint256 balanceAfter = getERC20OrETHBalance(erc20Address);

            require(
                balanceAfter - balanceBefore == amount,
                "proofless deposit balances must be equal"
            );
        }
    }
```

**File:** contracts/HinkalHelper.sol (L64-76)
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
