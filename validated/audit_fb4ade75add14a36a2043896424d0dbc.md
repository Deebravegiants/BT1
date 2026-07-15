I need to trace the full attack path carefully before rendering a verdict.

### Title
Unauthenticated CATWallet-to-CRCATWallet Conversion via Crafted On-Chain CRCAT Coin — (`chia/wallet/wallet_state_manager.py`)

---

### Summary

An unprivileged attacker who owns any amount of a victim's CAT asset can craft an on-chain coin spend that causes the victim's wallet to irreversibly convert its `CATWallet` to a `CRCATWallet` with attacker-controlled `authorized_providers` and `proofs_checker`. No victim key material is required. The conversion permanently corrupts the victim's wallet state and renders existing CAT coin records inaccessible through the wallet UI.

---

### Finding Description

The call chain is:

```
_add_coin_states  →  determine_coin_type  →  handle_cat  →  CRCATWallet.convert_to_cr
```

**Step 1 — Entry via hint subscription.**
The wallet subscribes to puzzle hashes as hints. When a coin is created with a hint matching a victim puzzle hash, the full node delivers a `CoinState` to the wallet. The attacker sets the hint of their crafted CRCAT coin to a known victim puzzle hash (observable on-chain from any prior transaction to the victim). [1](#0-0) 

**Step 2 — `determine_coin_type` fetches the parent spend.**
The parent coin spend is fetched from the peer. The parent must pass `match_cat_puzzle` with the victim's `asset_id`. The attacker achieves this by spending their own CAT coins (purchased on the open market for any publicly traded CAT). [2](#0-1) 

**Step 3 — `CRCAT.get_next_from_coin_spend` with attacker-controlled params.**
When the parent spend is a plain CAT (not already a CR-CAT), `get_next_from_coin_spend` looks for a REMARK condition (opcode `1`) in the inner puzzle's output conditions to extract `new_inner_puzzle_hash`, `authorized_providers`, and `proofs_checker`. The attacker fully controls the inner puzzle and solution of their CAT coin, so they can emit any REMARK condition they choose. [3](#0-2) 

**Step 4 — Coin identity check at line 1273 is satisfiable.**
The code requires `crcat.coin == coin_state.coin`. The CRCAT coin's puzzle hash is deterministically computed from the attacker-controlled `authorized_providers`, `proofs_checker`, and `new_inner_puzzle_hash`. The attacker pre-computes this hash and creates the coin with exactly that puzzle hash via the CREATE_COIN condition in their spend. The on-chain coin therefore matches. [4](#0-3) 

**Step 5 — Inner puzzle hash guard is bypassable via the pending approval state.**
The guard at lines 1280–1289 requires `crcat.inner_puzzle_hash` to either be in the victim's puzzle store OR equal `construct_pending_approval_state(hinted_coin.hint, coin_state.coin.amount).get_tree_hash()`. The attacker sets `new_inner_puzzle_hash` (via the REMARK condition) to exactly this pending approval state hash, computed from the victim's hint and the coin amount — both of which the attacker controls. [5](#0-4) 

**Step 6 — Conversion is triggered unconditionally.**
With no existing CRCAT wallet for this `asset_id`, the code finds the victim's matching `CATWallet` and calls `CRCATWallet.convert_to_cr` with the attacker-supplied `authorized_providers` and `proofs_checker`. There is no user confirmation, no signature check, and no ownership verification of the credential parameters. [6](#0-5) 

**Step 7 — `convert_to_cr` is irreversible.**
`convert_to_cr` overwrites the wallet record in the DB and replaces the in-memory wallet object. The existing CAT coin records remain in the coin store with `coin_type = CoinType.NORMAL`, but the CRCAT wallet queries exclusively for `CoinType.CRCAT` coins, so the victim's existing CAT balance becomes invisible to the wallet UI. [7](#0-6) [8](#0-7) 

---

### Impact Explanation

- The victim's `CATWallet` is permanently converted to a `CRCATWallet` with attacker-controlled `authorized_providers` and `proofs_checker`.
- Existing CAT coin records (stored as `CoinType.NORMAL`) are no longer returned by the CRCAT wallet's coin queries, making the victim's existing CAT balance inaccessible through the wallet UI.
- Any future CRCAT coins of this asset type sent to the victim will require a VC from the attacker's authorized providers to spend.
- The conversion cannot be undone through the wallet UI.

This matches: **High — Corruption of wallet sync state and coin records with direct security impact**, and **High — Permanent inability for the wallet to process valid spend bundles under normal network assumptions**.

---

### Likelihood Explanation

- Requires the attacker to own any nonzero amount of the target CAT (purchasable on DEXes for any publicly traded CAT such as USDS or SBX).
- Requires knowing one victim puzzle hash (observable from any prior on-chain transaction to the victim).
- Requires no victim keys, no admin access, and no broken cryptography.
- The crafted spend bundle is a valid on-chain transaction that passes full-node consensus validation.
- Likelihood is **Medium-High** for any victim holding a publicly traded CAT.

---

### Recommendation

1. **Do not auto-convert a `CATWallet` to `CRCATWallet` based solely on observed on-chain coin structure.** Conversion should require explicit user confirmation or be gated on a user-initiated action.
2. **Validate that the `authorized_providers` and `proofs_checker` in the observed CRCAT coin match a pre-approved policy** before triggering conversion.
3. **Consider requiring that the converting coin be owned by the victim** (i.e., the inner puzzle hash must be directly in the victim's puzzle store, not merely the pending approval state) before triggering wallet type conversion.
4. At minimum, add a guard that refuses conversion if the victim's existing `CATWallet` already has unspent coin records, preventing silent loss of access to existing funds.

---

### Proof of Concept

```python
# Attacker setup:
# - victim_puzzle_hash: known from on-chain observation
# - victim_asset_id: the TAIL hash of the victim's CATWallet
# - attacker_cat_coin: attacker's own CAT coin with victim_asset_id
# - attacker_providers: [attacker_did_id]  (attacker-controlled)
# - attacker_proofs_checker: ProofsChecker(["attacker_flag"]).as_program()

amount = uint64(1000)
pending_hash = construct_pending_approval_state(victim_puzzle_hash, amount).get_tree_hash()

# Compute the CRCAT puzzle hash the attacker will create
crcat_inner_hash = construct_cr_layer(
    attacker_providers, attacker_proofs_checker, pending_hash
).get_tree_hash_precalc(pending_hash)
crcat_puzzle_hash = construct_cat_puzzle(
    CAT_MOD, victim_asset_id, crcat_inner_hash
).get_tree_hash_precalc(crcat_inner_hash)

# Inner puzzle outputs:
# 1. CREATE_COIN(crcat_puzzle_hash, amount, [victim_puzzle_hash])  <- hint triggers wallet subscription
# 2. REMARK(pending_hash, attacker_providers, attacker_proofs_checker)  <- opcode 1, read by get_next_from_coin_spend
inner_puzzle = Program.to((1, [
    [51, crcat_puzzle_hash, amount, [victim_puzzle_hash]],
    [1, pending_hash, attacker_providers, attacker_proofs_checker],
]))

# Spend attacker's CAT coin with this inner puzzle
# Submit to mempool → confirmed on-chain
# Victim's wallet syncs → handle_cat fires → CATWallet converted to CRCATWallet
# with attacker_providers and attacker_proofs_checker
# Victim's existing CAT balance: 0 (invisible to CRCAT wallet queries)
```

### Citations

**File:** chia/wallet/wallet_state_manager.py (L917-942)
```python
        coin_spend = await fetch_coin_spend_for_coin_state(parent_coin_state, peer)

        uncurried = uncurry_puzzle(coin_spend.puzzle_reveal)

        # Check if the coin is a CAT
        cat_curried_args = match_cat_puzzle(uncurried)
        if cat_curried_args is not None:
            cat_mod_hash, tail_program_hash, cat_inner_puzzle = cat_curried_args
            cat_data: CATCoinData = CATCoinData(
                bytes32(cat_mod_hash.as_atom()),
                bytes32(tail_program_hash.as_atom()),
                cat_inner_puzzle,
                parent_coin_state.coin.parent_coin_info,
                uint64(parent_coin_state.coin.amount),
            )
            return (
                await self.handle_cat(
                    cat_data,
                    parent_coin_state,
                    coin_state,
                    coin_spend,
                    peer,
                    fork_height,
                ),
                cat_data,
            )
```

**File:** chia/wallet/wallet_state_manager.py (L1246-1252)
```python
        hinted_coin = compute_spend_hints_and_additions(coin_spend)[0][coin_state.coin.name()]
        assert hinted_coin.hint is not None, f"hint missing for coin {hinted_coin.coin}"
        derivation_record = await self.puzzle_store.get_derivation_record_for_puzzle_hash(hinted_coin.hint)

        if derivation_record is None:
            self.log.info(f"Received state for the coin that doesn't belong to us {coin_state}")
            return None
```

**File:** chia/wallet/wallet_state_manager.py (L1273-1275)
```python
                    crcat = next(crc for crc in next_crcats if crc.coin == coin_state.coin)

                    wallet_type = CRCATWallet
```

**File:** chia/wallet/wallet_state_manager.py (L1280-1289)
```python
                if (
                    await self.puzzle_store.get_derivation_record_for_puzzle_hash(crcat.inner_puzzle_hash) is None
                    and crcat.inner_puzzle_hash
                    != construct_pending_approval_state(
                        hinted_coin.hint,
                        uint64(coin_state.coin.amount),
                    ).get_tree_hash()
                ):
                    self.log.error(f"Unknown CRCAT inner puzzle, coin ID:{crcat.coin.name().hex()}")  # pragma: no cover
                    return None  # pragma: no cover
```

**File:** chia/wallet/wallet_state_manager.py (L1297-1312)
```python
            if wallet_type in {CRCATWallet, RCATWallet}:
                # We didn't find a matching alt-CAT wallet, but maybe we have a matching CAT wallet that we can convert
                for wallet_info in await self.get_all_wallet_info_entries(wallet_type=WalletType.CAT):
                    cat_info: CATInfo = CATInfo.from_bytes(bytes.fromhex(wallet_info.data))
                    found_cat_wallet = self.wallets[wallet_info.id]
                    assert isinstance(found_cat_wallet, CATWallet)
                    if cat_info.limitations_program_hash == asset_id:
                        if wallet_type is CRCATWallet:
                            assert crcat  # again, mypy isn't this smart
                            await CRCATWallet.convert_to_cr(
                                found_cat_wallet,
                                crcat.authorized_providers,
                                ProofsChecker.from_program(uncurry_puzzle(crcat.proofs_checker)),
                            )
                            self.state_changed("converted cat wallet to cr", wallet_info.id)
                            return WalletIdentifier(wallet_info.id, WalletType(WalletType.CRCAT))
```

**File:** chia/wallet/vc_wallet/cr_cat_drivers.py (L345-362)
```python
        if potential_cr_layer.uncurry()[0].uncurry()[0] != CREDENTIAL_RESTRICTION:
            # If the previous spend is not a CR-CAT:
            # we look for a remark condition that tells us the authorized_providers and proofs_checker
            inner_solution: Program = solution.at("f")
            if conditions is None:
                conditions = potential_cr_layer.run(inner_solution)
            for condition in conditions.as_iter():
                if condition.at("f") == Program.to(1):
                    new_inner_puzzle_hash = bytes32(condition.at("rf").as_atom())
                    authorized_providers_as_prog: Program = condition.at("rrf")
                    proofs_checker: Program = condition.at("rrrf")
                    break
            else:
                raise ValueError(
                    "Previous spend was not a CR-CAT, nor did it properly remark the CR params"
                )  # pragma: no cover
            authorized_providers = [bytes32(p.as_atom()) for p in authorized_providers_as_prog.as_iter()]
            lineage_inner_puzhash: bytes32 = potential_cr_layer.get_tree_hash()
```

**File:** chia/wallet/vc_wallet/cr_cat_wallet.py (L169-193)
```python
    @classmethod
    async def convert_to_cr(
        cls,
        cat_wallet: CATWallet,
        authorized_providers: list[bytes32],
        proofs_checker: ProofsChecker,
    ) -> None:
        replace_self = cls()
        replace_self.standard_wallet = cat_wallet.standard_wallet
        replace_self.log = logging.getLogger(cat_wallet.get_name())
        replace_self.log.info(f"Converting CAT wallet {cat_wallet.id()} to CR-CAT wallet")
        replace_self.wallet_state_manager = cat_wallet.wallet_state_manager
        replace_self.info = cls.wallet_info_type(
            cat_wallet.cat_info.limitations_program_hash, None, authorized_providers, proofs_checker
        )
        await cat_wallet.wallet_state_manager.user_store.update_wallet(
            WalletInfo(
                cat_wallet.id(), cat_wallet.get_name(), uint8(WalletType.CRCAT.value), bytes(replace_self.info).hex()
            )
        )
        updated_wallet_info = await cat_wallet.wallet_state_manager.user_store.get_wallet_by_id(cat_wallet.id())
        assert updated_wallet_info is not None
        replace_self.wallet_info = updated_wallet_info

        cat_wallet.wallet_state_manager.wallets[cat_wallet.id()] = replace_self
```

**File:** chia/wallet/vc_wallet/cr_cat_wallet.py (L327-332)
```python
    async def get_confirmed_balance(self, record_list: set[WalletCoinRecord] | None = None) -> uint128:
        if record_list is None:
            record_list = await self.wallet_state_manager.coin_store.get_unspent_coins_for_wallet(
                self.id(), CoinType.CRCAT
            )
        amount: uint128 = uint128(0)
```
