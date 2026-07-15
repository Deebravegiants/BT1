### Title
Pool Operator Can Indefinitely Block User's Exit from `LEAVING_POOL` State via Repeated Reward Absorption - (`chia/pools/pool_puzzles.py`, `chia/pools/pool_wallet.py`)

### Summary

The Chia pool singleton's waiting-room puzzle enforces the exit delay using `ASSERT_HEIGHT_RELATIVE relative_lock_height`, which is relative to the **current singleton coin's creation height**. Because the pool protocol permits reward absorption (`create_absorb_spend`) while the singleton is in `LEAVING_POOL` state — and each absorption spends the current singleton coin and creates a new one at a higher block height — a malicious pool operator can repeatedly absorb farming rewards to continuously reset the relative-height countdown, permanently blocking the user from completing the exit transition.

### Finding Description

When a user initiates leaving a pool, the singleton transitions to `LEAVING_POOL` state and the inner puzzle becomes the waiting-room puzzle (`POOL_WAITING_ROOM_MOD`), curried with `relative_lock_height`: [1](#0-0) 

The exit spend is only valid after `ASSERT_HEIGHT_RELATIVE relative_lock_height` blocks have elapsed since the **current singleton coin's creation height**. This is enforced on-chain by the CLVM puzzle.

The pool protocol explicitly supports reward absorption while in `LEAVING_POOL` state. `create_absorb_spend` handles the waiting-room case: [2](#0-1) 

Each absorb spend **spends the current singleton coin and creates a new one** at the current block height. The new coin's creation height becomes the new baseline for `ASSERT_HEIGHT_RELATIVE`. This is confirmed by the lifecycle test which explicitly exercises "ABSORB WHILE IN WAITING ROOM": [3](#0-2) 

The wallet-level exit trigger in `new_peak` also uses `tip_height` (the height of the most recent singleton spend) to compute when the user can exit: [4](#0-3) 

Every pool absorb updates `tip_height`, resetting `leave_height = tip_height + relative_lock_height` at both the wallet layer and the CLVM layer simultaneously.

The absorb spend requires no signature from the user — the pool only needs the public singleton state and the p2_singleton coins (both visible on-chain): [5](#0-4) 

### Impact Explanation

A malicious pool operator can prevent a user from ever completing the `LEAVING_POOL → SELF_POOLING` (or `LEAVING_POOL → FARMING_TO_POOL`) transition by absorbing any farming reward that accumulates at the `p2_singleton_puzzle_hash` while the user is in the waiting room. Each absorption resets the `ASSERT_HEIGHT_RELATIVE` countdown. The user's singleton is permanently stuck in `LEAVING_POOL` state as long as farming rewards are available. The user cannot join a new pool, cannot self-pool, and cannot exercise any singleton state transition. This maps to: **High — long-lived inability for the user to complete valid pool actions under normal network assumptions.**

The `MAXIMUM_RELATIVE_LOCK_HEIGHT = 1000` cap means the pool can set the maximum allowed lock height at join time, maximizing the reset window per absorb: [6](#0-5) 

### Likelihood Explanation

The pool operator is a semi-trusted party. A malicious pool can execute this attack silently — absorb spends are valid, fee-free (when `fee=0`), and require no user interaction. The attack is sustained as long as the user's plots continue farming blocks to the `p2_singleton_puzzle_hash`. The user has no on-chain recourse; their only mitigation is to stop farming entirely, sacrificing farming income.

### Recommendation

- Replace `ASSERT_HEIGHT_RELATIVE` in the waiting-room puzzle with `ASSERT_HEIGHT_ABSOLUTE` anchored to the block height of the original `LEAVING_POOL` spend, so that reward absorptions cannot reset the countdown.
- Alternatively, record the `LEAVING_POOL` spend height in the singleton state and enforce the absolute exit height in the puzzle, making it immune to absorb-based resets.
- At minimum, document that users should stop farming when in `LEAVING_POOL` state to prevent pool-driven countdown resets.

### Proof of Concept

1. User joins pool with `relative_lock_height = 1000` (maximum allowed by `MAXIMUM_RELATIVE_LOCK_HEIGHT`).
2. User calls `pw_self_pool()` → singleton enters `LEAVING_POOL` at block height H. Exit requires block H + 1000.
3. User continues farming; rewards accumulate at `p2_singleton_puzzle_hash`.
4. At block H + 999, pool calls `create_absorb_spend` with the waiting-room singleton. A new singleton coin is created at height H + 999.
5. Exit now requires block (H + 999) + 1000 = H + 1999.
6. Pool repeats step 4 every ~999 blocks indefinitely.
7. The user's singleton never exits `LEAVING_POOL`; `new_peak` never triggers the second travel transaction because `peak_height > leave_height + 2` is never satisfied for long enough. [7](#0-6) [8](#0-7)

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

**File:** chia/pools/pool_wallet.py (L69-70)
```python
    MINIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 5
    MAXIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 1000
```

**File:** chia/pools/pool_wallet.py (L807-826)
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
```
