### Title
Malicious Peer Can Corrupt NFT Wallet State via Unvalidated Coin Spend Solution — (`chia/wallet/wallet_state_manager.py`, `chia/wallet/util/wallet_sync_utils.py`)

---

### Summary

`handle_nft` in `WalletStateManager` derives `new_p2_puzhash` from the peer-supplied spend solution, which is never validated against the actual on-chain spend. A malicious peer can return a crafted solution encoding an attacker-controlled `new_p2_puzhash`, causing the wallet to remove the old NFT coin record without adding the new one, permanently losing track of an NFT the wallet still owns.

---

### Finding Description

The call chain is:

1. **`determine_coin_type`** receives a `coin_state` for a new NFT child coin (coin B) and fetches the parent coin state and spend from the peer. [1](#0-0) 

2. **`fetch_coin_spend`** validates only the puzzle hash — it checks `puzzle.get_tree_hash() == coin.puzzle_hash` — but the **solution is accepted verbatim from the peer with no validation**. [2](#0-1) 

3. **`handle_nft`** extracts `old_p2_puzhash` from the puzzle (validated) and `new_p2_puzhash` from the peer-supplied solution (unvalidated): [3](#0-2) 

4. If `old_derivation_record is not None` (wallet owns the NFT) and `parent_coin_state.spent_height is not None`, `remove_coin` is called on the old NFT coin: [4](#0-3) 

5. Because `new_derivation_record is None` (attacker's address is not in the wallet), no new wallet or coin record is created. The wallet loses coin B entirely. [5](#0-4) 

6. Additionally, if the NFT wallet is DID-linked and now empty, `delete_wallet` is triggered: [6](#0-5) 

---

### Impact Explanation

The wallet permanently loses track of an NFT it still owns on-chain. Because `add_coin` is never called for coin B, the wallet never calls `add_interested_coin_ids([coin_B.name()])`, so it will not receive future spend updates for coin B either. The NFT is effectively invisible to the wallet until a full resync or manual `find_lost_nft`. This is direct corruption of wallet sync state and NFT coin records with security impact (inability to spend or transfer the NFT).

---

### Likelihood Explanation

The wallet connects to arbitrary peers on the Chia network. Any peer the wallet connects to can execute this attack. The only precondition is that the NFT's parent coin must be spent (so `spent_height is not None`), which is satisfied whenever the wallet itself transfers or updates the NFT, or when the attacker can cause the NFT to be spent. The puzzle hash validation in `fetch_coin_spend` is not a barrier — the peer returns the correct puzzle (its hash is public once the coin is spent) and only crafts the solution.

---

### Recommendation

Validate the spend solution against the actual on-chain output. After fetching the coin spend, execute the puzzle with the solution using the CLVM and verify that the computed additions match the actual child coin(s) observed on-chain (i.e., the `coin_state` that triggered `determine_coin_type`). Specifically, `compute_additions(coin_spend)` should produce a coin whose puzzle hash matches `coin_state.coin.puzzle_hash`. This check would make it impossible for a peer to supply a solution that produces a different `new_p2_puzhash` than what is actually on-chain.

---

### Proof of Concept

**Setup**: Wallet W owns NFT coin A (singleton launcher ID X, `old_p2_puzhash` = W's derivation address). W spends coin A on-chain (e.g., metadata update), producing coin B (still owned by W).

**Attack**:
1. Attacker operates a malicious full node peer P.
2. W connects to P and receives a `coin_state` for coin B (hinted with X).
3. W calls `determine_coin_type` → fetches parent coin state for coin A from P (P returns `spent_height` = real block height).
4. W calls `fetch_coin_spend` for coin A → P returns the correct puzzle (hash-validated) but a crafted solution where `new_p2_puzhash` = attacker's address.
5. `handle_nft` runs: `old_derivation_record` is found (W owns coin A), `new_derivation_record` is None (attacker's address not in W's puzzle store).
6. `remove_coin(coin_A)` is called → coin A deleted from NFT store.
7. No new coin record is created for coin B.
8. W is not subscribed to coin B; it will never receive future updates for it.

**Assert**: W's NFT store no longer contains the NFT. W cannot spend or transfer it. If the NFT wallet was DID-linked and this was its only NFT, the wallet is also deleted.

### Citations

**File:** chia/wallet/wallet_state_manager.py (L908-917)
```python
        response: list[CoinState] = await self.wallet_node.get_coin_state(
            [coin_state.coin.parent_coin_info], peer=peer, fork_height=fork_height
        )
        if len(response) == 0:
            self.log.warning(f"Could not find a parent coin with ID: {coin_state.coin.parent_coin_info.hex()}")
            return None, None
        parent_coin_state = response[0]
        assert parent_coin_state.spent_height == coin_state.created_height

        coin_spend = await fetch_coin_spend_for_coin_state(parent_coin_state, peer)
```

**File:** chia/wallet/wallet_state_manager.py (L1544-1548)
```python
        old_p2_puzhash = uncurried_nft.p2_puzzle.get_tree_hash()
        _metadata, new_p2_puzhash = get_metadata_and_phs(
            uncurried_nft,
            nft_data.parent_coin_spend.solution,
        )
```

**File:** chia/wallet/wallet_state_manager.py (L1574-1579)
```python
        if new_derivation_record is None and old_derivation_record is None:
            self.log.debug(
                "Cannot find a P2 puzzle hash for NFT:%s, this NFT belongs to others.",
                uncurried_nft.singleton_launcher_id.hex(),
            )
            return wallet_identifier
```

**File:** chia/wallet/wallet_state_manager.py (L1583-1592)
```python
            if nft_wallet.nft_wallet_info.did_id == old_did_id and old_derivation_record is not None:
                self.log.info(
                    "Removing old NFT, NFT_ID:%s, DID_ID:%s",
                    uncurried_nft.singleton_launcher_id.hex(),
                    old_did_id,
                )
                if nft_data.parent_coin_state.spent_height is not None:
                    await nft_wallet.remove_coin(
                        nft_data.parent_coin_spend.coin, uint32(nft_data.parent_coin_state.spent_height)
                    )
```

**File:** chia/wallet/util/wallet_sync_utils.py (L343-352)
```python
    if solution_response.response.puzzle.get_tree_hash() != coin.puzzle_hash:
        raise PeerRequestException(f"Peer returned wrong puzzle hash for coin {coin_id}")
    if solution_response.response.coin_name != coin_id:
        raise PeerRequestException(f"Peer returned wrong coin name in puzzle solution for coin {coin_id}")

    return make_spend(
        coin,
        solution_response.response.puzzle,
        solution_response.response.solution,
    )
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L287-298)
```python
            if num == 0 and self.did_id is not None:
                # Check if the wallet owns the DID
                for did_wallet in await self.wallet_state_manager.get_all_wallet_info_entries(
                    wallet_type=WalletType.DECENTRALIZED_ID
                ):
                    did_wallet_info: DIDInfo = DIDInfo.from_json_dict(json.loads(did_wallet.data))
                    assert did_wallet_info.origin_coin is not None
                    if did_wallet_info.origin_coin.name() == self.did_id:
                        return
                self.log.info(f"No NFT, deleting wallet {self.wallet_info.name} ...")
                await self.wallet_state_manager.delete_wallet(self.wallet_info.id)
                self.wallet_state_manager.wallets.pop(self.wallet_info.id)
```
