### Title
Duplicate `address(0)` entries in `circomData.erc20TokenAddresses` cause `msg.value` to be credited once per entry, minting unbacked shielded ETH - (File: `contracts/Hinkal.sol`)

### Finding Description
The claimed equality is: **total ETH actually received by the contract (`msg.value`) must equal exactly one term in the balance equation** for the whole transaction, i.e. `Σ over all ETH-denominated slots of (amountChanges[i] + utxoAmount[i])` must not exceed the single real ETH inflow.

`Hinkal.transact` iterates `circomData.erc20TokenAddresses` and, for every index whose token is `address(0)`, computes
```solidity
balanceDif = int256(newBalances[i]) + int256(msg.value) - int256(oldBalances[i]);
``` [1](#0-0) 
and then requires `balanceDif == amountChanges[i] + utxoAmount[i]` per index [2](#0-1) .

Neither `dimensionsCheck` nor any other check enforces that `circomData.erc20TokenAddresses` entries are unique — it only verifies array *lengths* match `dimensions.tokenNumber` [3](#0-2) . Nothing in `performHinkalChecks` or `checkOnchainCreation` rejects repeated `address(0)` slots either [4](#0-3) .

If an attacker crafts `erc20TokenAddresses = [address(0), address(0), ...]` (two or more ETH slots) with `onChainCreation[i] = false` and `amountChanges[i] = X` for each duplicated slot, and sends `msg.value = X`:

1. Because `oldBalances` is captured *after* the ETH already landed in the contract (payable increments balance before the function body runs) and `_internalTransact`'s deposit branch for ETH only performs a **stateless comparison** `require(msg.value == _value)` in `transferERC20TokenFromOrCheckETH` without actually moving/consuming any ETH [5](#0-4) , this check passes independently and repeatedly for every duplicated slot with the same `msg.value`, since the value is never “spent” or decremented.
2. `oldBalances[i]` and `newBalances[i]` are identical for both duplicate indices (same address queried at the same two points in time), so the *real* ETH delta contributed by each is `0`.
3. The outer loop then independently re-adds the **full** `msg.value` to each duplicate index: `balanceDif0 = 0 + msg.value = X` and `balanceDif1 = 0 + msg.value = X`.
4. Each index's `require(balanceDif == amountChanges[i] + utxoAmount[i])` is satisfied independently with `amountChanges[i] = X`, so the contract accepts **two** separate `X`-ETH deposit claims backed by only **one** real `X`-ETH transfer.
5. The circuit-side constraint `inTotal[i] + amountChanges[i] === outTotal[i]` operates per-slot and does not tie the two ETH slots together or forbid `erc20TokenAddresses[i]` from repeating across slots, so the attacker can generate a fully valid honest proof (with `inTotal=0` and two independent output UTXOs of value `X` each denominated in ETH) that will pass `verifyProof`.

The net effect: the attacker deposits `X` wei of ETH but the contract creates/authorizes off-chain UTXOs (or on-chain commitments) worth `2X` in shielded ETH, because the same `msg.value` backs two accounting terms.

### Impact Explanation
This mints unbacked shielded ETH — an attacker gets `2X` (or `nX` for `n` duplicated slots) of shielded value for `X` real ETH deposited, directly draining the pool's real ETH backing over subsequent withdrawals. This is a Critical finding: minting shielded value without backing / protocol insolvency, repeatable on every call with as many duplicate slots as `dimensions.tokenNumber` allows.

### Likelihood Explanation
No privileged role is required. The attacker only needs to: (a) choose `dimensions.tokenNumber ≥ 2`, (b) set two or more `erc20TokenAddresses` entries to `address(0)`, (c) set matching `amountChanges[i] = X` for each duplicate, (d) send `msg.value = X`, and (e) generate a locally-valid proof for their own crafted UTXOs (fully within attacker capabilities per the rules). No hook, malicious relay, or TOCTOU window is actually required — duplicate slots alone trigger the double count, though a hook could additionally be used to further manipulate `newBalances` if desired. This is straightforward and repeatable indefinitely.

### Recommendation
- In `dimensionsCheck` (or a new validation step in `performHinkalChecks`), require that `circomData.erc20TokenAddresses` contains no duplicate addresses.
- Alternatively/additionally, redesign the balance-equation loop in `Hinkal.transact` to add `msg.value` to the aggregate ETH accounting exactly once (e.g., accumulate a single `ethCredited` flag/variable across the loop rather than adding `msg.value` unconditionally inside each per-index branch), and make `transferERC20TokenFromOrCheckETH`'s ETH check decrement a running "remaining msg.value" counter instead of doing a stateless equality check that can be satisfied multiple times.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal` with real verifier disabled/mocked only for local proof generation (attacker still generates a valid proof off-chain as per rules — not a proof bypass).
2. Build `circomData` with `dimensions.tokenNumber = 2`, `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [X, X]`, `onChainCreation = [false, false]`, `slippageValues = [X, X]`, two fresh output UTXOs each of value `X` and token `address(0)`, `inputNullifiers` empty/zero (fresh deposit), `externalActionData.externalActionId = 0`, `externalActionData.externalAddress = attacker`.
3. Generate a valid proof for this `circomData` locally.
4. Call `hinkal.transact{value: X}(a, b, c, dimensions, circomData)`.
5. Assert: `address(hinkal).balance` increased by exactly `X` (real ETH received), while the sum of newly inserted UTXO/commitment values for token `address(0)` equals `2*X`.
6. Assert the broken equality directly: `mintedShieldedETH (2*X) > realETHDelta (X)`, proving unbacked minting.

### Citations

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

**File:** contracts/Hinkal.sol (L134-146)
```text
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

**File:** contracts/HinkalHelper.sol (L173-236)
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

    ///@notice make performance checks for transactions
    ///@dev Check if transacaction is valid before making it
    ///@param circomData circom data
    ///@return inputForCircom
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
