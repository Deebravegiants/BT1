### Title
Malicious Peer Can Fabricate DL Singleton Root via Unvalidated Solution in `singleton_removed` — (`chia/data_layer/data_layer_wallet.py`)

### Summary

`DataLayerWallet.singleton_removed` fetches a `CoinSpend` from a peer, validates only the puzzle reveal (against the coin's on-chain `puzzle_hash`), and then runs the puzzle with the peer-supplied **solution** via `run_with_cost` — which performs no signature verification. The `root` and `inner_puzzle_hash` stored in the resulting `SingletonRecord` are taken directly from the CREATE_COIN hint fields (`condition[3][1]`, `condition[3][2]`) without any cross-check against the actual child coin's puzzle hash. A malicious peer can serve a crafted solution whose delegated puzzle emits a CREATE_COIN with an arbitrary hint, causing the wallet to permanently store a fabricated DL root.

---

### Finding Description

**Entry point** — `wallet_state_manager.py` lines 2124–2130:

```python
if record.wallet_type == WalletType.DATA_LAYER:
    singleton_spend = await fetch_coin_spend_for_coin_state(coin_state, peer)
    dl_wallet = self.get_wallet(id=uint32(record.wallet_id), required_type=DataLayerWallet)
    await dl_wallet.singleton_removed(singleton_spend, uint32(coin_state.spent_height))
``` [1](#0-0) 

**`fetch_coin_spend` validates the puzzle but not the solution** — `wallet_sync_utils.py` lines 336–352:

```python
if solution_response.response.puzzle.get_tree_hash() != coin.puzzle_hash:
    raise PeerRequestException(f"Peer returned wrong puzzle hash for coin {coin_id}")
# solution is accepted as-is, no on-chain validation
``` [2](#0-1) 

**`singleton_removed` trusts hint fields from peer-supplied solution** — `data_layer_wallet.py` lines 819–856:

```python
conditions = run_with_cost(puzzle, self.wallet_state_manager.constants.MAX_BLOCK_COST_CLVM, solution)[1].as_python()
for condition in conditions:
    if condition[0] == ConditionOpcode.CREATE_COIN and int.from_bytes(condition[2], "big") % 2 == 1:
        full_puzzle_hash = bytes32(condition[1])
        amount = uint64(int.from_bytes(condition[2], "big"))
        root = bytes32(condition[3][1])           # ← taken from hint, no verification
        inner_puzzle_hash = bytes32(condition[3][2])  # ← taken from hint, no verification
``` [3](#0-2) 

The fabricated values are then persisted unconditionally:

```python
await self.wallet_state_manager.dl_store.add_singleton_record(
    SingletonRecord(
        coin_id=new_singleton.name(),
        root=root,                    # ← attacker-controlled
        inner_puzzle_hash=inner_puzzle_hash,  # ← attacker-controlled
        ...
    )
)
``` [4](#0-3) 

**Why `run_with_cost` accepts the crafted solution**: For a standard DL singleton, the inner puzzle is a p2_delegated_puzzle. Its solution is `(delegated_puzzle, solution, hidden_puzzle)`. The p2 puzzle runs the delegated puzzle and appends `AGG_SIG_ME`, but `run_with_cost` performs **no signature verification** — it only executes CLVM. A peer can supply a delegated puzzle that emits `(CREATE_COIN <correct_full_puzzle_hash> <odd_amount> (<launcher_id> <fake_root> <fake_inner_puzzle_hash>))`. The singleton top layer enforces odd amount and singleton structure but does **not** enforce the hint content. The CLVM execution succeeds, and the fabricated hints are extracted. [5](#0-4) 

---

### Impact Explanation

The `SingletonRecord.root` stored in `dl_store` diverges from the root actually committed in the child coin's on-chain puzzle hash. Consequences:

1. **Data Layer clients** querying the wallet's RPC for the current DL root receive a forged value, breaking data integrity guarantees.
2. **Future spends fail**: `create_update_state_spend` reconstructs the current puzzle using `singleton_record.root` and `singleton_record.inner_puzzle_hash`. With fabricated values, the reconstructed puzzle hash won't match the actual on-chain coin, making the wallet unable to produce valid spends for that singleton.
3. The `lineage_proof` stored alongside also uses the fabricated values (`create_host_layer_puzzle(inner_puzzle_hash, root).get_tree_hash_precalc(inner_puzzle_hash)`), compounding the corruption.

This maps to: **High — Corruption of Data Layer root/store state with direct security impact**.

---

### Likelihood Explanation

The attacker must control a full node peer that the wallet connects to (or perform a MITM on the connection). Chia wallets connect to full node peers and, for untrusted peers, validate coin states against header blocks — but **do not validate puzzle solutions**. Running a public full node that wallets connect to is a realistic, low-barrier capability. No private keys or admin access are required.

---

### Recommendation

After fetching the `CoinSpend`, cross-validate the extracted `root` and `inner_puzzle_hash` against the actual child coin's puzzle hash before storing:

```python
expected_full_puz_hash = create_host_fullpuz(inner_puzzle_hash, root, singleton_record.launcher_id).get_tree_hash_precalc(inner_puzzle_hash)
if full_puzzle_hash != expected_full_puz_hash:
    self.log.warning("Peer returned solution with hints inconsistent with child coin puzzle hash")
    return
```

This ensures the stored `root`/`inner_puzzle_hash` are consistent with what is actually committed on-chain in the child coin's puzzle hash, regardless of what the peer claims in the hint.

---

### Proof of Concept

```python
# Attacker controls a peer. Wallet tracks a DL singleton with coin C (spent on-chain).
# Peer serves:
#   puzzle_reveal = actual DL singleton puzzle for C (must match C.puzzle_hash)
#   solution = crafted solution where delegated_puzzle emits:
#     (CREATE_COIN actual_child_puzzle_hash odd_amount
#       (launcher_id FAKE_ROOT FAKE_INNER_PUZZLE_HASH))

# In singleton_removed:
#   run_with_cost(puzzle, MAX_COST, crafted_solution) succeeds (no sig check)
#   condition[3][1] = FAKE_ROOT
#   condition[3][2] = FAKE_INNER_PUZZLE_HASH
#   add_singleton_record stores these fabricated values

# Assert:
stored = await dl_store.get_latest_singleton(launcher_id)
assert stored.root == FAKE_ROOT  # diverges from actual on-chain root
actual_root = <root curried into child coin's puzzle>
assert stored.root != actual_root  # invariant violated
```

### Citations

**File:** chia/wallet/wallet_state_manager.py (L2124-2130)
```python
                        if record.wallet_type == WalletType.DATA_LAYER:
                            singleton_spend = await fetch_coin_spend_for_coin_state(coin_state, peer)
                            dl_wallet = self.get_wallet(id=uint32(record.wallet_id), required_type=DataLayerWallet)
                            await dl_wallet.singleton_removed(
                                singleton_spend,
                                uint32(coin_state.spent_height),
                            )
```

**File:** chia/wallet/util/wallet_sync_utils.py (L336-352)
```python
async def fetch_coin_spend(height: uint32, coin: Coin, peer: WSChiaConnection) -> CoinSpend:
    solution_response = await peer.call_api(
        FullNodeAPI.request_puzzle_solution, RequestPuzzleSolution(coin.name(), height)
    )
    if solution_response is None or not isinstance(solution_response, RespondPuzzleSolution):
        raise PeerRequestException(f"Was not able to obtain solution {solution_response}")
    coin_id = coin.name()
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

**File:** chia/data_layer/data_layer_wallet.py (L819-861)
```python
            conditions = run_with_cost(puzzle, self.wallet_state_manager.constants.MAX_BLOCK_COST_CLVM, solution)[
                1
            ].as_python()
            found_singleton: bool = False
            for condition in conditions:
                if condition[0] == ConditionOpcode.CREATE_COIN and int.from_bytes(condition[2], "big") % 2 == 1:
                    full_puzzle_hash = bytes32(condition[1])
                    amount = uint64(int.from_bytes(condition[2], "big"))
                    try:
                        root = bytes32(condition[3][1])
                        inner_puzzle_hash = bytes32(condition[3][2])
                    except IndexError:
                        self.log.warning(
                            f"Parent {parent_name} with launcher {singleton_record.launcher_id} "
                            "did not hint its child properly"
                        )
                        return
                    found_singleton = True
                    break

            if not found_singleton:
                self.log.warning(f"Singleton with launcher ID {singleton_record.launcher_id} was melted")
                return

            new_singleton = Coin(parent_name, full_puzzle_hash, amount)
            timestamp = await self.wallet_state_manager.wallet_node.get_timestamp_for_height(height)
            await self.wallet_state_manager.dl_store.add_singleton_record(
                SingletonRecord(
                    coin_id=new_singleton.name(),
                    launcher_id=singleton_record.launcher_id,
                    root=root,
                    inner_puzzle_hash=inner_puzzle_hash,
                    confirmed=True,
                    confirmed_at_height=height,
                    timestamp=timestamp,
                    lineage_proof=LineageProof(
                        parent_name,
                        create_host_layer_puzzle(inner_puzzle_hash, root).get_tree_hash_precalc(inner_puzzle_hash),
                        amount,
                    ),
                    generation=uint32(singleton_record.generation + 1),
                )
            )
```

**File:** chia/wallet/db_wallet/db_wallet_puzzles.py (L43-56)
```python
def match_dl_singleton(puzzle: Program | SerializedProgram) -> tuple[bool, Iterator[Program]]:
    """
    Given a puzzle test if it's a CAT and, if it is, return the curried arguments
    """
    mod, singleton_curried_args = uncurry(puzzle)
    if mod == SINGLETON_TOP_LAYER_MOD:
        mod, dl_curried_args = uncurry(singleton_curried_args.at("rf"))
        if mod == NFT_STATE_LAYER_MOD and dl_curried_args.at("rrf") == ACS_MU_PH:
            launcher_id = singleton_curried_args.at("frf")
            root = dl_curried_args.at("rff")
            innerpuz = dl_curried_args.at("rrrf")
            return True, iter((innerpuz, root, launcher_id))

    return False, iter(())
```
