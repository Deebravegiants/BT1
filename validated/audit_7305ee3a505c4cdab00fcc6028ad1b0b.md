### Title
Shared, unowned Emporium balance ("stranded shares") can be swept by any later CASE 2 caller via `handleOut`'s blind balance-delta accounting - ([File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol])

### Summary
When a CASE 2 (stateless) Emporium operation mints vault/LP shares to the `Emporium` contract itself and the depositor does not redeem/withdraw them within the same `transact()` call (i.e. omits the share token from `circomData.erc20TokenAddresses`), those shares sit in `Emporium`'s own token balance with no on-chain record of who they belong to. Because `runAction`/`handleOut` attribute *any* positive balance delta observed during a transaction entirely to whichever `msg.sender` triggers it, and ERC4626-style `redeem()`/`donate()` distributes value pro-rata across all outstanding shares, the next attacker who crafts a CASE 2 operation redeeming those (or any inflated) shares receives the entire windfall as a freshly minted, fully backed UTXO.

### Finding Description
Broken equality: `utxo_minted_to_redeemer` (value shielded via `handleOut`) should equal `victim_original_principal` (the value the legitimate depositor is owed), but in this attack it equals `victim_original_principal + arbitrary_third_party_donation`, with none of it verified against any prior depositor's proof.

Code path:
1. A user (or attacker acting as "victim" for setup) deposits into a vault via `Hinkal.transact()` with `externalActionId` = Emporium's id, using a CASE 2 op (`invokeWallet == false`) whose `callData` calls `vault.deposit(...)`, with `receiver = emporium` (since the low-level `.call` in `EmporiumUpgradeable.runAction` at [1](#0-0)  executes with `msg.sender == Emporium`). If the depositor's `circomData.erc20TokenAddresses` for that transaction does not include the vault-share token, `handleOut` is never invoked for that token, so the minted shares remain in `Emporium`'s raw ERC20 balance, unlinked to any UTXO or nullifier.
2. A third, unrelated actor donates directly to the vault (e.g. `vault.donate()` or a direct transfer increasing `totalAssets` per share), inflating the redeemable value of every existing share, including the stranded ones held by `Emporium`.
3. The attacker submits their own `Hinkal.transact()` with a CASE 2 Emporium op whose `callData` calls `vault.redeem(sharesHeldByEmporium, emporium, emporium)` - valid because `Emporium` is both `msg.sender` and share owner in an ERC4626 call context. This pulls the underlying asset (victim's principal + donation windfall) into `Emporium`.
4. `runAction` computes `balanceChange = balancesAfter[i] - balancesBefore[i]` for that asset [2](#0-1) , which captures the *entire* redeemed amount (nothing here distinguishes "this attacker's contribution" from "value already sitting in Emporium from someone else"). `handleOut` then transfers that whole amount to `msg.sender` (`Hinkal.sol`) and mints a UTXO for it, tied to the attacker's own stealth address [3](#0-2) .
5. Back in `Hinkal.transact()`, the balance-conservation check only verifies internal consistency of `Hinkal.sol`'s own balance versus `amountChanges` + `utxoAmount` [4](#0-3) ; it has no way to verify that `utxoAmount` corresponds to value the attacker actually deposited from their own spent nullifiers/UTXOs, so it passes trivially since `utxoAmount` is exactly what `handleOut` transferred.

Why existing guards fail: `performHinkalChecks`, `verifyProof`, `rootHashExists`, `insertNullifiers`, and the circuit's `inTotal + amountChanges === outTotal` constraint all correctly bind the attacker's *own* spent/created UTXOs to their proof - but none of them constrain what an *external call* does with `Emporium`'s pre-existing shared token balance. The vulnerability lives entirely in the trust boundary between "value Emporium held before this call" and "value Emporium receives during this call": the code conflates the two into a single `balanceChange` and credits it wholesale to whoever calls `runAction` next. This matches the documented design intent that CASE 1 (stateful, via `HinkalWallet`) is meant for persistent per-user positions, while CASE 2 (stateless) is meant to be atomic within a single transaction - the code does not enforce this atomicity, allowing value to be stranded in the shared `Emporium` contract and later swept by an unrelated party.

### Impact Explanation
Any value left in `Emporium`'s raw token balance across transactions (from an incomplete CASE 2 deposit, a stray transfer, or a third-party donation to a vault Emporium holds shares in) can be captured entirely by the next attacker who triggers a positive `balanceChange` for that token via a crafted CASE 2 op. This is direct theft of another party's principal (not just windfall) - misattribution of ownership over value held by `Emporium`, satisfying the Critical bar ("direct theft of shielded or in-flight user funds... minting shielded value without backing"). It is repeatable against any token/vault combination where CASE 2 is used non-atomically, and requires no privileged role - only crafting `externalActionMetadata`/`CircomData` fields, which the attacker fully controls.

### Likelihood Explanation
Preconditions: (1) some value must already be resting in `Emporium`'s balance for a given ERC20 (from a non-atomic CASE 2 deposit by any user, or a donation to a vault Emporium holds shares in), and (2) the target vault/contract must allow `Emporium` (as `msg.sender`) to redeem/claim that value via a stateless call. Both are realistic given that CASE 2 is explicitly supported for arbitrary `endpoint.call` interactions and nothing in `Hinkal.sol`/`EmporiumUpgradeable.sol` forces atomic deposit+withdraw pairing. Attacker cost is a single `transact()` call with a self-generated proof for their own (even zero-value) UTXO; the payoff can be arbitrarily larger than their cost, and the attack is repeatable each time stranded value reappears.

### Recommendation
Do not allow value to persist in the shared, stateless `Emporium` contract across transactions. Either (a) enforce atomicity for CASE 2 operations by requiring `circomData.erc20TokenAddresses` to include every token whose balance changes as a result of the ops (so `handleOut` always sweeps/shields the resulting balance in the same transaction it is created), or (b) require CASE 2 external positions (vault shares, LP tokens) to be routed through per-user `HinkalWallet` proxies (CASE 1) instead of leaving them on the shared `Emporium` balance, or (c) explicitly track ownership of any token balance left on `Emporium` between transactions (e.g., an internal ledger keyed by depositor) rather than inferring ownership purely from `balanceChange` deltas observed by whoever calls next.

### Proof of Concept
Foundry test outline:
1. Deploy a mock ERC4626 vault with a `donate()`/direct-transfer path that increases `totalAssets` without minting new shares.
2. Victim calls `Hinkal.transact()` with a CASE 2 Emporium op calling `vault.deposit(amount, emporium)`, declaring only the underlying asset in `erc20TokenAddresses` (omitting the share token) - assert `IERC20(vaultShare).balanceOf(emporium) == sharesMinted` and no UTXO was created for the share token.
3. A third-party address (not via Hinkal) calls `vault.donate(donationAmount)` directly, inflating `vault.convertToAssets(sharesMinted)` beyond the victim's original deposit.
4. Attacker calls `Hinkal.transact()` with a CASE 2 op calling `vault.redeem(sharesMinted, emporium, emporium)`, declaring the underlying asset in `erc20TokenAddresses`.
5. Assert: the UTXO minted to the attacker (`utxoAmount`/`balanceChange` from `handleOut`) equals `victim_original_principal + donationAmount`, i.e. `utxo_minted_to_redeemer > victim_original_principal`, proving `assets_claimable_by_UTXO_holder != assets_actually_owed_to_original_depositor`.
6. Assert `IERC20(vaultShare).balanceOf(emporium) == 0` afterward and that no nullifier/proof from the victim was consumed or referenced in step 4's transaction.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-144)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
```text
    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
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
