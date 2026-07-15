### Title
Pool Absorb Spend Resets `ASSERT_HEIGHT_RELATIVE` Timer, Allowing Pool to Permanently Trap Farmer in `LEAVING_POOL` State — (File: chia/pools/pool_puzzles.py)

---

### Summary

When a farmer enters `LEAVING_POOL` state, the pool (or any third party) can prevent the farmer from ever completing the exit by repeatedly submitting absorb spends. Each absorb spend spends the current singleton coin and creates a new one at the current block height, resetting the `ASSERT_HEIGHT_RELATIVE` timer that enforces `relative_lock_height`. Because absorb spends in `LEAVING_POOL` state require no farmer signature, the pool can submit them without the farmer's consent whenever a farming reward coin exists.

---

### Finding Description

The pool singleton exit mechanism works as follows:

1. The farmer transitions from `FARMING_TO_POOL` → `LEAVING_POOL` by spending the singleton with a travel spend.
2. The singleton is now governed by the waiting-room inner puzzle (`POOL_WAITINGROOM_INNERPUZ`), which enforces `ASSERT_HEIGHT_RELATIVE relative_lock_height` on the exit spend path.
3. `ASSERT_HEIGHT_RELATIVE N` checks `current_block_height − coin_creation_height ≥ N`. The coin's creation height is the height at which the singleton was last spent.
4. The farmer must wait `relative_lock_height` blocks after the singleton was last spent before the exit spend is valid.

The waiting-room puzzle also has an **absorb path** (spend_type = 0) that allows claiming farming rewards while in `LEAVING_POOL` state: [1](#0-0) 

```python
elif is_pool_waitingroom_inner_puzzle(inner_puzzle):
    inner_sol = Program.to([0, reward_amount, height])
```

This absorb spend:
- Spends the current singleton coin (created at height H).
- Creates a **new** singleton coin at the current block height H′.
- Uses `G2Element()` (empty signature) — **no farmer authorization required**. [2](#0-1) 

The new singleton coin's creation height is H′. The next exit spend's `ASSERT_HEIGHT_RELATIVE` check is now relative to H′, not the original height when `LEAVING_POOL` was entered. The timer is fully reset.

Since absorb spends are permissionless (confirmed by the test using `SpendBundle(coin_sols, G2Element())`), the pool can submit them without the farmer's knowledge or consent. The pool only needs:
- The singleton's current on-chain state (public).
- The block height at which the farmer won a farming reward (public, via `pool_parent_id(height, genesis_challenge)`). [3](#0-2) 

---

### Impact Explanation

A malicious pool can permanently prevent a farmer from completing the `LEAVING_POOL` → `SELF_POOLING` (or `FARMING_TO_POOL` at a new pool) transition:

1. Farmer enters `LEAVING_POOL` at block H. `relative_lock_height` = 1440 (≈1 day on mainnet).
2. Farmer wins a block at H+100, creating a `p2_singleton` reward coin.
3. Pool immediately submits an absorb spend at H+100. New singleton created at H+100.
4. Farmer must now wait until H+100+1440 = H+1540 to exit.
5. Farmer wins another block at H+1439. Pool submits absorb spend. New singleton at H+1439.
6. Farmer must now wait until H+1439+1440 = H+2879.
7. Repeat indefinitely.

As long as the farmer continues farming (which is expected — they are in a pool), the pool can keep resetting the timer. The farmer is permanently trapped in `LEAVING_POOL` state and cannot redirect rewards to a new pool or self-pool.

This matches the allowed High impact: **"Permanent or long-lived inability for honest farmers to process pool actions."** [4](#0-3) 

---

### Likelihood Explanation

- Any active farmer in a pool wins blocks regularly (proportional to their plot space).
- The pool operator has full visibility into on-chain state and can automate absorb spend submission.
- No special privileges, leaked keys, or cryptographic breaks are required.
- The only prerequisite is that the farmer wins at least one block during each `relative_lock_height` window, which is expected for any non-trivial farmer.

---

### Recommendation

The root cause is that `ASSERT_HEIGHT_RELATIVE` is anchored to the **most recently spent singleton coin**, which changes on every absorb spend. Two mitigations:

1. **Record the `LEAVING_POOL` entry height in the singleton state** and use `ASSERT_HEIGHT_ABSOLUTE (entry_height + relative_lock_height)` for the exit condition. This makes the timer independent of subsequent absorb spends.

2. **Disallow absorb spends in `LEAVING_POOL` state** after the `relative_lock_height` window has started. The pool's legitimate interest (claiming outstanding rewards) can be served by requiring all absorb spends to complete before the farmer initiates the exit, or by using a separate claim mechanism that does not re-create the singleton coin. [5](#0-4) [6](#0-5) 

---

### Proof of Concept

The existing test suite already demonstrates absorb spends in `LEAVING_POOL` state succeed with an empty signature: [2](#0-1) 

And the exit spend fails with `ASSERT_HEIGHT_RELATIVE_FAILED` if the timer has not elapsed: [7](#0-6) 

Attack sequence:
1. Farmer calls `pw_self_pool()` → singleton enters `LEAVING_POOL` at block H.
2. Pool monitors `p2_singleton_puzzle_hash` for incoming reward coins.
3. On each reward coin, pool constructs `create_absorb_spend(last_coin_spend, target_pool_state, launcher_coin, reward_height, ...)` and submits `SpendBundle(coin_sols, G2Element())`.
4. Each submission resets the singleton's creation height to the current block.
5. The farmer's `pw_self_pool()` second-stage travel transaction (submitted by `new_peak()` in `pool_wallet.py`) is perpetually blocked by `ASSERT_HEIGHT_RELATIVE_FAILED`. [8](#0-7)

### Citations

**File:** chia/pools/pool_puzzles.py (L51-64)
```python
def create_waiting_room_inner_puzzle(
    target_puzzle_hash: bytes32,
    relative_lock_height: uint32,
    owner_pubkey: G1Element,
    launcher_id: bytes32,
    genesis_challenge: bytes32,
    delay_time: uint64,
    delay_ph: bytes32,
) -> Program:
    pool_reward_prefix = bytes32(genesis_challenge[:16] + b"\x00" * 16)
    p2_singleton_puzzle_hash: bytes32 = launcher_id_to_p2_puzzle_hash(launcher_id, delay_time, delay_ph)
    return POOL_WAITING_ROOM_MOD.curry(
        target_puzzle_hash, p2_singleton_puzzle_hash, bytes(owner_pubkey), pool_reward_prefix, relative_lock_height
    )
```

**File:** chia/pools/pool_puzzles.py (L252-308)
```python
def create_absorb_spend(
    last_coin_spend: CoinSpend,
    current_state: PoolState,
    launcher_coin: Coin,
    height: uint32,
    genesis_challenge: bytes32,
    delay_time: uint64,
    delay_ph: bytes32,
) -> list[CoinSpend]:
    inner_puzzle: Program = pool_state_to_inner_puzzle(
        current_state, launcher_coin.name(), genesis_challenge, delay_time, delay_ph
    )
    reward_amount: uint64 = calculate_pool_reward(height)
    if is_pool_member_inner_puzzle(inner_puzzle):
        # inner sol is (spend_type, pool_reward_amount, pool_reward_height, extra_data)
        inner_sol: Program = Program.to([reward_amount, height])
    elif is_pool_waitingroom_inner_puzzle(inner_puzzle):
        # inner sol is (spend_type, destination_puzhash, pool_reward_amount, pool_reward_height, extra_data)
        inner_sol = Program.to([0, reward_amount, height])
    else:
        raise ValueError
    # full sol = (parent_info, my_amount, inner_solution)
    coin: Coin | None = get_most_recent_singleton_coin_from_coin_spend(last_coin_spend)
    assert coin is not None

    if coin.parent_coin_info == launcher_coin.name():
        parent_info: Program = Program.to([launcher_coin.parent_coin_info, launcher_coin.amount])
    else:
        p = Program.from_bytes(bytes(last_coin_spend.puzzle_reveal))
        last_coin_spend_inner_puzzle: Program | None = get_inner_puzzle_from_puzzle(p)
        assert last_coin_spend_inner_puzzle is not None
        parent_info = Program.to(
            [
                last_coin_spend.coin.parent_coin_info,
                last_coin_spend_inner_puzzle.get_tree_hash(),
                last_coin_spend.coin.amount,
            ]
        )
    full_solution: SerializedProgram = SerializedProgram.to([parent_info, last_coin_spend.coin.amount, inner_sol])
    full_puzzle: SerializedProgram = create_full_puzzle(inner_puzzle, launcher_coin.name()).to_serialized()
    assert coin.puzzle_hash == full_puzzle.get_tree_hash()

    reward_parent: bytes32 = pool_parent_id(height, genesis_challenge)
    p2_singleton_puzzle = create_p2_singleton_puzzle(
        SINGLETON_MOD_HASH, launcher_coin.name(), delay_time, delay_ph
    ).to_serialized()
    reward_coin: Coin = Coin(reward_parent, p2_singleton_puzzle.get_tree_hash(), reward_amount)
    p2_singleton_solution = SerializedProgram.to([inner_puzzle.get_tree_hash(), reward_coin.name()])
    assert p2_singleton_puzzle.get_tree_hash() == reward_coin.puzzle_hash
    assert full_puzzle.get_tree_hash() == coin.puzzle_hash
    assert get_inner_puzzle_from_puzzle(Program.from_bytes(bytes(full_puzzle))) is not None

    coin_spends = [
        CoinSpend(coin, full_puzzle, full_solution),
        CoinSpend(reward_coin, p2_singleton_puzzle, p2_singleton_solution),
    ]
    return coin_spends
```

**File:** chia/_tests/pools/test_pool_puzzles_lifecycle.py (L326-333)
```python
        # Spend it and hope it fails!
        with pytest.raises(
            BadSpendBundleError,
            match=re.escape(f"condition validation failure {Err.ASSERT_HEIGHT_RELATIVE_FAILED!s}"),
        ):
            coin_db.update_coin_store_for_spend_bundle(
                SpendBundle([return_coinsol], sig), time, DEFAULT_CONSTANTS.MAX_BLOCK_COST_CLVM
            )
```

**File:** chia/_tests/pools/test_pool_puzzles_lifecycle.py (L335-352)
```python
        # ABSORB WHILE IN WAITING ROOM
        time = CoinTimestamp(10000060, 3)
        # create the farming reward
        coin_db.farm_coin(p2_singleton_ph, time, 1750000000000)
        # generate relevant coin solutions
        coin_sols: list[CoinSpend] = create_absorb_spend(
            travel_coinsol,
            target_pool_state,
            launcher_coin,
            3,
            GENESIS_CHALLENGE,
            DELAY_TIME,
            DELAY_PH,  # height
        )
        # Spend it!
        coin_db.update_coin_store_for_spend_bundle(
            SpendBundle(coin_sols, G2Element()), time, DEFAULT_CONSTANTS.MAX_BLOCK_COST_CLVM
        )
```

**File:** chia/pools/pool_wallet.py (L807-850)
```python
    async def new_peak(self, peak_height: uint32) -> None:
        # This gets called from the WalletStateManager whenever there is a new peak

        pool_wallet_info: PoolWalletInfo = await self.get_current_state()
        tip_height, tip_spend = await self.get_tip()

        if self.target_state is None:
            return
        if self.target_state == pool_wallet_info.current:
            self.target_state = None
            raise ValueError(f"Internal error. Pool wallet {self.wallet_id} state: {pool_wallet_info.current}")

        if (
            self.target_state.state in {FARMING_TO_POOL.value, SELF_POOLING.value}
            and pool_wallet_info.current.state == LEAVING_POOL.value
        ):
            leave_height = tip_height + pool_wallet_info.current.relative_lock_height

            # Add some buffer (+2) to reduce chances of a reorg
            if peak_height > leave_height + 2:
                unconfirmed: list[
                    TransactionRecord
                ] = await self.wallet_state_manager.tx_store.get_unconfirmed_for_wallet(self.wallet_id)
                next_tip: Coin | None = get_most_recent_singleton_coin_from_coin_spend(tip_spend)
                assert next_tip is not None

                if any([rem.name() == next_tip.name() for tx_rec in unconfirmed for rem in tx_rec.removals]):
                    self.log.info("Already submitted second transaction, will not resubmit.")
                    return

                self.log.info(f"Attempting to leave from\n{pool_wallet_info.current}\nto\n{self.target_state}")
                assert self.target_state.version == POOL_PROTOCOL_VERSION
                assert pool_wallet_info.current.state == LEAVING_POOL.value
                assert self.target_state.target_puzzle_hash is not None

                if self.target_state.state == SELF_POOLING.value:
                    assert self.target_state.relative_lock_height == 0
                    assert self.target_state.pool_url is None
                elif self.target_state.state == FARMING_TO_POOL.value:
                    assert self.target_state.relative_lock_height >= self.MINIMUM_RELATIVE_LOCK_HEIGHT
                    assert self.target_state.pool_url is not None

                async with self.wallet_state_manager.new_action_scope(self.next_tx_config, push=True) as action_scope:
                    await self.generate_travel_transactions(self.next_transaction_fee, action_scope)
```

**File:** chia/pools/pool_wallet_info.py (L42-60)
```python
class PoolState(Streamable):
    """
    `PoolState` is a type that is serialized to the blockchain to track the state of the user's pool singleton
    `target_puzzle_hash` is either the pool address, or the self-pooling address that pool rewards will be paid to.
    `target_puzzle_hash` is NOT the p2_singleton puzzle that block rewards are sent to.
    The `p2_singleton` address is the initial address, and the `target_puzzle_hash` is the final destination.
    `relative_lock_height` is zero when in SELF_POOLING state
    """

    version: uint8
    state: uint8  # PoolSingletonState
    # `target_puzzle_hash`: A puzzle_hash we pay to
    # When self-farming, this is a main wallet address
    # When farming-to-pool, the pool sends this to the farmer during pool protocol setup
    target_puzzle_hash: bytes32  # TODO: rename target_puzzle_hash -> pay_to_address
    # owner_pubkey is set by the wallet, once
    owner_pubkey: G1Element
    pool_url: str | None
    relative_lock_height: uint32
```
