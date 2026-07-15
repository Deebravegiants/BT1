Let me look at the exact guard logic in `handle_cat` and the `get_next_from_coin_spend` parsing to confirm the full attack path.

The attack path is fully traceable. Here is the complete analysis:

---

### Title
Attacker-Controlled `proofs_checker` Permanently Corrupts Victim's CATWallet via Unchecked `convert_to_cr` Conversion — (`chia/wallet/wallet_state_manager.py`)

### Summary
An unprivileged attacker can send a crafted CRCAT coin to a victim who holds a plain `CATWallet` for the same asset ID. During wallet sync, `handle_cat` unconditionally calls `CRCATWallet.convert_to_cr` using the attacker-supplied `authorized_providers` and `proofs_checker` extracted from the coin's puzzle reveal. No validation is performed against any expected or pre-configured values. The victim's `CATWallet` is permanently overwritten in the database with attacker-controlled CRCAT parameters.

### Finding Description

**Step 1 — Attacker crafts the coin.**

The attacker creates a valid CRCAT coin on-chain with:
- The same `tail_hash` (asset ID) as the victim's existing `CATWallet`
- An attacker-chosen `proofs_checker` (e.g., `PROOF_FLAGS_CHECKER.curry([])` — zero required flags)
- Attacker-chosen `authorized_providers`
- The hint set to the victim's known inner puzzle hash (so `derivation_record` is non-`None`)
- The CRCAT inner puzzle hash set to the victim's puzzle hash (so the inner puzzle ownership check at lines 1280–1289 passes)

**Step 2 — `handle_cat` processes the coin.** [1](#0-0) 

`CRCAT.get_next_from_coin_spend` parses `authorized_providers` and `proofs_checker` directly from the puzzle reveal with no validation: [2](#0-1) 

**Step 3 — The early-exit guard only checks for existing CRCAT wallets.** [3](#0-2) 

If the victim has only a plain `CATWallet` (not yet a `CRCATWallet`), this loop finds nothing and falls through.

**Step 4 — `convert_to_cr` is called with attacker-controlled values, no validation.** [4](#0-3) 

`convert_to_cr` unconditionally overwrites the wallet record: [5](#0-4) 

There is no check that the incoming `authorized_providers` or `proofs_checker` match any expected configuration. The database record is permanently replaced.

### Impact Explanation

The victim's `CATWallet` is permanently converted to a `CRCATWallet` with attacker-controlled `authorized_providers` and `proofs_checker`. After this:

- The wallet's local state no longer matches the actual on-chain coins the victim holds (which are plain CATs, not CRCATs).
- The wallet will attempt to spend the victim's existing plain CAT coins as CRCATs, requiring VC authorization that does not exist for those coins — effectively locking the victim out of their funds through the normal wallet interface.
- The corruption persists in the database until the victim restores from seed.

**Clarification on the claimed impact:** The specific claim that "the attacker can spend CRCATs without valid credentials" is **incorrect**. The on-chain CRCAT puzzle enforces credential checks at the consensus level regardless of wallet state. The actual impact is **wallet sync state corruption with direct security impact** — the victim loses the ability to spend their existing CAT coins through the wallet software.

### Likelihood Explanation

- The attacker only needs the victim's public address (hint = victim's puzzle hash), which is observable on-chain.
- Creating a valid CRCAT on-chain requires only XCH for fees — no special privileges.
- The attack triggers automatically during the victim's next wallet sync with no user interaction required.
- The attack is a one-shot permanent corruption; subsequent syncs return early at line 1292–1295 (existing CRCAT wallet found).

### Recommendation

In `handle_cat`, before calling `convert_to_cr`, validate that the incoming `authorized_providers` and `proofs_checker` match the values the user originally configured for that asset ID (if any such configuration exists). At minimum, require explicit user confirmation before converting a `CATWallet` to a `CRCATWallet` based on an inbound coin's puzzle parameters. The conversion should never be driven unilaterally by attacker-supplied on-chain data.

### Proof of Concept

```python
# Attacker constructs a CRCAT with permissive proofs_checker targeting victim's asset_id
permissive_proofs_checker = PROOF_FLAGS_CHECKER.curry([])  # zero required flags
attacker_providers = [attacker_did_id]

dpuz, launch_spend, crcat = CRCAT.launch(
    origin_coin,
    CreateCoin(victim_puzzle_hash, amount),  # hint = victim's inner puzzle hash
    Program.NIL,
    Program.NIL,
    attacker_providers,
    permissive_proofs_checker,
)
# Push to chain. On victim's next sync:
# handle_cat -> get_next_from_coin_spend (reads attacker's proofs_checker from puzzle)
# -> no existing CRCATWallet found -> convert_to_cr called with attacker's params
# -> victim's CATWallet permanently overwritten in DB
```

After sync, `victim_wallet.info.proofs_checker` equals `ProofsChecker([])` and `victim_wallet.info.authorized_providers` equals `[attacker_did_id]`, regardless of what the victim originally configured.

### Citations

**File:** chia/wallet/wallet_state_manager.py (L1266-1275)
```python
                else:
                    try:
                        next_crcats = CRCAT.get_next_from_coin_spend(coin_spend)

                    except ValueError:
                        return None

                    crcat = next(crc for crc in next_crcats if crc.coin == coin_state.coin)

                    wallet_type = CRCATWallet
```

**File:** chia/wallet/wallet_state_manager.py (L1291-1295)
```python
                # Check if we already have a wallet
                for wallet_info in await self.get_all_wallet_info_entries(wallet_type=WalletType.CRCAT):
                    crcat_info: CRCATInfo = CRCATInfo.from_bytes(bytes.fromhex(wallet_info.data))
                    if crcat_info.limitations_program_hash == asset_id:
                        return WalletIdentifier(wallet_info.id, WalletType(wallet_info.type))
```

**File:** chia/wallet/wallet_state_manager.py (L1303-1312)
```python
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

**File:** chia/wallet/vc_wallet/cr_cat_drivers.py (L363-377)
```python
        else:
            # Otherwise the info we need will be in the puzzle reveal
            cr_first_curry, self_hash_and_innerpuz = potential_cr_layer.uncurry()
            _, authorized_providers_as_prog, proofs_checker = cr_first_curry.uncurry()[1].as_iter()
            _, inner_puzzle = self_hash_and_innerpuz.as_iter()
            inner_solution = solution.at("f").at("rrrrrrf")
            if conditions is None:
                conditions = inner_puzzle.run(inner_solution)
            inner_puzzle_hash: bytes32 = inner_puzzle.get_tree_hash()
            authorized_providers = [bytes32(p.as_atom()) for p in authorized_providers_as_prog.as_iter()]
            lineage_inner_puzhash = construct_cr_layer(
                authorized_providers,
                proofs_checker,
                inner_puzzle_hash,  # type: ignore
            ).get_tree_hash_precalc(inner_puzzle_hash)
```

**File:** chia/wallet/vc_wallet/cr_cat_wallet.py (L181-193)
```python
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
