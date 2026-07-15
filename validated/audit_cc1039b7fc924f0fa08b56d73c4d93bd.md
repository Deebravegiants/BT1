### Title
Unprivileged On-Chain CRCAT Coin Triggers Irreversible CAT Wallet Type Overwrite via Missing Existence Guard — (`chia/wallet/wallet_state_manager.py`)

---

### Summary

`handle_cat()` in `WalletStateManager` unconditionally converts an existing `CATWallet` to a `CRCATWallet` when a CRCAT coin hinting to the victim's puzzle hash is observed on-chain, using attacker-controlled `authorized_providers` and `proofs_checker` extracted from the coin spend. There is no guard preventing this conversion when the CAT wallet already holds coins, and no ownership verification of the triggering coin. Any unprivileged actor who holds any amount of the target CAT can execute this attack by spending their CAT to produce a CRCAT output hinting to the victim's puzzle hash.

---

### Finding Description

In `handle_cat()`, after confirming the hint matches a derivation record in the victim's wallet, the code checks whether the coin is a CRCAT: [1](#0-0) 

If `wallet_type` resolves to `CRCATWallet`, the code first checks for an existing CRCAT wallet with the same `asset_id`: [2](#0-1) 

If none is found, it then searches for an existing **CAT** wallet with the same `limitations_program_hash` and, without any further guard, calls `convert_to_cr()` with the attacker-supplied parameters: [3](#0-2) 

`CRCATWallet.convert_to_cr()` permanently overwrites the wallet type in the DB and in memory, setting `authorized_providers` and `proofs_checker` to whatever the attacker embedded in the coin spend: [4](#0-3) 

Critically, unlike `RCATWallet.convert_to_revocable()` which refuses conversion if the lineage store is non-empty: [5](#0-4) 

`convert_to_cr()` has **no such guard** — it converts the wallet even when the victim holds existing CAT coins.

The inner-puzzle ownership check at lines 1280–1289 is bypassable: the attacker sets the CRCAT inner puzzle to `construct_pending_approval_state(victim_puzzle_hash, amount)`, which the check explicitly allows: [6](#0-5) 

---

### Impact Explanation

After conversion, the victim's wallet is a `CRCATWallet` whose `info.authorized_providers` and `info.proofs_checker` are attacker-controlled. Spending any CAT coin through the wallet now routes through `CRCATWallet._generate_unsigned_spendbundle()`, which requires a VC issued by one of the `authorized_providers`: [7](#0-6) 

Since the victim has no VC from the attacker's provider, the wallet raises `RuntimeError("CR-CATs cannot be spent without an appropriate VC")` on every spend attempt. The victim's existing on-chain CAT coins (which are regular CATs, not CRCATs) are effectively locked inside a wallet that can no longer generate valid spends for them. The DB change is permanent — the wallet type is overwritten via `INSERT or REPLACE`: [8](#0-7) 

This constitutes corruption of wallet sync state and coin control with direct security impact (victim's CAT balance is inaccessible through the wallet).

---

### Likelihood Explanation

The attacker needs only to:
1. Hold any nonzero amount of the target CAT (purchasable on any DEX).
2. Derive the victim's puzzle hash from their on-chain public key (public information).
3. Spend their CAT to produce a CRCAT output with `inner_puzzle = construct_pending_approval_state(victim_puzzle_hash, amount)`, malicious `authorized_providers`, and `hint = victim_puzzle_hash`.

The full node delivers this coin state to the victim's wallet via the hint subscription mechanism. No privileged access, leaked keys, or cryptographic break is required. The cost is a small on-chain transaction fee plus the dust amount of the CAT.

---

### Recommendation

1. **In `CRCATWallet.convert_to_cr()`**: Add the same lineage-store guard present in `convert_to_revocable()` — refuse conversion if the CAT wallet's lineage store is non-empty (i.e., the wallet already holds coins).

2. **In `handle_cat()`** (lines 1304–1312): Before calling `convert_to_cr()`, verify that the triggering CRCAT coin's inner puzzle hash (not just the pending-approval state) is actually controlled by the local wallet's key material. The pending-approval bypass at lines 1282–1286 should not be sufficient to authorize a wallet-type overwrite.

3. **Consider requiring explicit user confirmation** before any automatic CAT→CRCAT wallet conversion, since this is an irreversible state change affecting coin spendability.

---

### Proof of Concept

```
1. Victim holds CAT wallet (TAIL hash = X) with 1000 CAT coins.

2. Attacker buys 1 mojo of CAT X on a DEX.

3. Attacker constructs a spend bundle:
   - Spends their 1-mojo CAT X coin
   - Creates a CRCAT output:
       tail_hash          = X
       inner_puzzle       = construct_pending_approval_state(victim_puzzle_hash, 1)
       authorized_providers = [attacker_did]
       proofs_checker     = ProofsChecker(["impossible_flag"])
       hint               = victim_puzzle_hash
   - Total supply unchanged → TAIL program not invoked

4. Spend bundle is accepted on-chain.

5. Full node delivers coin state to victim's wallet (hint subscription).

6. _add_coin_states → determine_coin_type → handle_cat:
   - hint matches victim's derivation record ✓
   - puzzle_hash ≠ standard CAT puzzle → CRCAT branch taken
   - inner_puzzle == pending_approval_state(victim_puzzle_hash) → ownership check passes
   - No existing CRCAT wallet for asset_id X found
   - Existing CAT wallet for asset_id X found → convert_to_cr() called

7. convert_to_cr() overwrites DB:
   wallet_type  = CRCAT
   authorized_providers = [attacker_did]
   proofs_checker = requires "impossible_flag"

8. Victim attempts to send CAT X:
   → CRCATWallet._generate_unsigned_spendbundle()
   → RuntimeError: "CR-CATs cannot be spent without an appropriate VC"
   → Victim's 1000 CAT coins are inaccessible through the wallet.
```

### Citations

**File:** chia/wallet/wallet_state_manager.py (L1258-1275)
```python
            if cat_puzzle.get_tree_hash() != coin_state.coin.puzzle_hash:
                # Check if it is a special type of CAT
                uncurried_puzzle_reveal = uncurry_puzzle(coin_spend.puzzle_reveal)
                if uncurried_puzzle_reveal.mod != CAT_MOD:
                    return None
                revocation_layer_match = match_revocation_layer(uncurry_puzzle(uncurried_puzzle_reveal.args.at("rrf")))
                if revocation_layer_match is not None:
                    wallet_type = RCATWallet
                else:
                    try:
                        next_crcats = CRCAT.get_next_from_coin_spend(coin_spend)

                    except ValueError:
                        return None

                    crcat = next(crc for crc in next_crcats if crc.coin == coin_state.coin)

                    wallet_type = CRCATWallet
```

**File:** chia/wallet/wallet_state_manager.py (L1276-1289)
```python
            if wallet_type is CRCATWallet:
                assert crcat  # mypy doesn't get the semantics
                # Since CRCAT wallet doesn't have derivation path, every CRCAT will go through this code path
                # Make sure we control the inner puzzle or we control it if it's wrapped in the pending state
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

**File:** chia/wallet/wallet_state_manager.py (L1291-1295)
```python
                # Check if we already have a wallet
                for wallet_info in await self.get_all_wallet_info_entries(wallet_type=WalletType.CRCAT):
                    crcat_info: CRCATInfo = CRCATInfo.from_bytes(bytes.fromhex(wallet_info.data))
                    if crcat_info.limitations_program_hash == asset_id:
                        return WalletIdentifier(wallet_info.id, WalletType(wallet_info.type))
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

**File:** chia/wallet/vc_wallet/cr_cat_wallet.py (L462-468)
```python
        for wallet in self.wallet_state_manager.wallets.values():
            if WalletType(wallet.type()) == WalletType.VC:
                assert isinstance(wallet, VCWallet)
                vc_wallet = wallet
                break
        else:
            raise RuntimeError("CR-CATs cannot be spent without an appropriate VC")  # pragma: no cover
```

**File:** chia/wallet/cat_wallet/r_cat_wallet.py (L160-167)
```python
    async def convert_to_revocable(
        cls,
        cat_wallet: CATWallet,
        hidden_puzzle_hash: bytes32,
    ) -> bool:
        if not await cat_wallet.lineage_store.is_empty():
            cat_wallet.log.error("Received a revocable CAT to a CAT wallet that already has CATs")
            return False
```

**File:** chia/wallet/wallet_user_store.py (L70-81)
```python
    async def update_wallet(self, wallet_info: WalletInfo) -> None:
        async with self.db_wrapper.writer_maybe_transaction() as conn:
            cursor = await conn.execute(
                "INSERT or REPLACE INTO users_wallets VALUES(?, ?, ?, ?)",
                (
                    wallet_info.id,
                    wallet_info.name,
                    wallet_info.type,
                    wallet_info.data,
                ),
            )
            await cursor.close()
```
