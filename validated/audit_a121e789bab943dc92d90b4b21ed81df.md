### Title
Attacker-controlled ERC20 balance mirroring lets `balanceDif` double-count a single ETH deposit as two independent tokens, minting unbacked shielded UTXOs - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.transact` snapshots per-token balances with `getBalancesForArray`/`getERC20OrETHBalance`, which for any non-zero `erc20TokenAddresses[i]` blindly calls `IERC20(erc20TokenAddresses[i]).balanceOf(address(this))` with no allowlist or independence check. An attacker who deploys their own "wrapped ETH" token whose `balanceOf()` simply mirrors `address(hinkal).balance` can make a single real ETH deposit satisfy the `balanceDif` equality for *two* distinct `erc20TokenAddresses` entries at once — the real `address(0)` entry and the attacker's fake mirror token entry — letting the attacker mint an on-chain UTXO for the fake token backed by zero incremental value.

### Finding Description
The claimed-safe invariant per token index `i` is:
```
balanceDif[i] == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount[i]
```
checked in `contracts/Hinkal.sol` lines 97-147: [1](#0-0) 

`balanceDif` is derived from `oldBalances`/`newBalances`, which come from `getBalancesForArray` → `getERC20OrETHBalance`: [2](#0-1) 

For `erc20TokenAddresses[i] == address(0)`, the ETH branch adds `msg.value` and reads `address(this).balance`; for any non-zero address it trusts an external `balanceOf()` call. There is no requirement that `erc20TokenAddresses` entries be distinct, real, independently-backed tokens, and no verification that a listed ERC20's `balanceOf` reflects genuine, separately-custodied reserves.

Exploit flow (using the LiFi swap external action, `contracts/external-actions/swaps/ExternalActionSwap.sol` and `LifiExternalAction.sol`):
1. Attacker deploys a malicious "wrapped-ETH-mirror" ERC20 token `FakeWETH` whose `balanceOf(hinkal)` simply returns `hinkal.balance` (i.e. proxies the very same native-ETH reserve that also backs the `address(0)` entry), rather than tracking an independent token balance.
2. Attacker builds a `transact` call with `erc20TokenAddresses = [address(0), FakeWETH]` (or vice versa) and `externalActionData` targeting `LifiExternalAction`. Index 0 (the real `address(0)` leg) is used normally as the swap input, funded from an actual ETH deposit/`amountChanges`. Index 1 (`FakeWETH`) is set with `onChainCreation[1] = true` and `amountChanges[1] = 0` (required by `checkOnchainCreation`, `contracts/HinkalHelper.sol` lines 173-202).
3. `callRouter` (in `LifiExternalAction.sol` lines 16-36) is invoked with attacker-crafted `externalActionMetadata` sent to the fixed router address; the attacker only needs this call to succeed (e.g. a harmless no-op call to the router), since `swappedAmount` is computed purely as `getERC20OrETHBalance(FakeWETH)` before/after — a value the attacker fully controls via their token's fake `balanceOf` logic.
4. Because `FakeWETH.balanceOf(hinkal)` mirrors `hinkal.balance`, the ETH increase already accounted for by the `address(0)` entry (from the real deposit) is *also* observed as an increase for the `FakeWETH` entry, satisfying `balanceDif[1] == 0 + utxoAmount` at line 137-146 without any real token ever entering Hinkal for that leg.
5. `ExternalActionSwap.swap` (lines 40-102) then mints a UTXO entry for `outputToken = FakeWETH` with `amount = amountToSendToHinkal`, which is inserted as a genuine shielded on-chain commitment via `insertCommitments` at line 161-166 of `Hinkal.sol`.

Existing guards do not catch this: `performHinkalChecks`, `dimensionsCheck`, and `checkOnchainCreation` only validate array-length consistency and that `amountChanges[i]==0`/`inputNullifiers` are zero when `onChainCreation[i]` is true — none of them validate that distinct `erc20TokenAddresses` entries correspond to economically independent assets. The circuit constraints (`inTotal + amountChanges === outTotal`, etc.) operate purely on the numeric public inputs and have no visibility into whether the EVM-side `balanceOf` call for a given token address is honest or an alias of another entry's balance.

### Impact Explanation
The attacker mints a shielded UTXO for `FakeWETH` that is not backed by any real transferred value beyond what was already credited to the `address(0)` entry — i.e., protocol insolvency: shielded value minted without backing. This directly matches the Critical category ("minting shielded value without backing"). The attack is repeatable for any amount the attacker is willing to route as ETH, and scales with each additional invocation, since the mirror token's `balanceOf` will reflect whatever the current real ETH reserve happens to be at call time.

### Likelihood Explanation
Preconditions are entirely attacker-controlled: deploying an arbitrary ERC20-like contract, listing it in `erc20TokenAddresses`, crafting `onChainCreation`/`amountChanges`/`slippageValues`, and generating a valid proof for their own inputs/outputs (all explicitly listed as attacker capabilities). No privileged role, relay cooperation, or victim interaction is required; the only external dependency is that the router call inside `callRouter` succeeds, which the attacker can arrange with benign calldata to the fixed router address. This makes the exploit low-cost and fully repeatable.

### Recommendation
Do not trust arbitrary `erc20TokenAddresses[i]` balances as independent economic signals. Options:
- Restrict `erc20TokenAddresses` to an on-chain allowlist of vetted, canonical token contracts (excluding contracts whose `balanceOf` is not backed by real transferred value).
- Require `erc20TokenAddresses` entries to be unique and reject a transaction where `address(0)` and any listed token could represent the same underlying reserve semantically (e.g., disallow arbitrary token registration for use in `onChainCreation` mints, or require a real transferAmount reconciliation independent of a queryable `balanceOf`).
- More fundamentally, redesign the balance-accounting to track token movements via `transfer`/`transferFrom` return values and explicit accounting rather than relying solely on before/after `balanceOf` snapshots of attacker-supplied contracts.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `LifiExternalAction` (with a mock router that accepts arbitrary calldata and returns success), and a `FakeWETH` contract whose `balanceOf(address who)` returns `who.balance` (i.e. mirrors native ETH balance instead of maintaining its own ledger).
2. Register `LifiExternalAction` via `registerExternalAction`.
3. Construct a `transact` call with `erc20TokenAddresses = [address(0), address(FakeWETH)]`, `amountChanges = [-X, 0]`, `onChainCreation = [false, true]`, `slippageValues` satisfied, and a valid Circom proof for these public inputs (generated locally with a test circuit/witness matching the values).
4. Send the call with `msg.value == X` so the swap input (`address(0)`) leg is funded and consumed by `ExternalActionSwap.swap`.
5. Have the mock router's call succeed without touching `FakeWETH`'s "balance" independently (since it's just `hinkal.balance`), so `swappedAmount` for `FakeWETH` naturally reflects the residual ETH balance change already accounted by the `address(0)` leg.
6. Assert: `balanceDif[1] == utxoAmount[1]` holds (transaction succeeds and mints the on-chain commitment) while the true net new value transferred into Hinkal is `X` (from step 4) but shielded value minted equals `X` (offchain leg) + `utxoAmount[1]` (onchain `FakeWETH` UTXO) > `X`, demonstrating `vault balance delta < credited UTXO value`.

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
