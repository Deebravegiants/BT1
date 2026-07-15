### Title
Permissionless Absorb Spend Resets Singleton Coin Height, Indefinitely Blocking Pool Exit — (`File: chia/pools/pool_puzzles.py`, `chia/pools/pool_wallet.py`)

---

### Summary

An unprivileged attacker can repeatedly trigger a permissionless absorb spend on a victim farmer's pool singleton while it is in `LEAVING_POOL` state. Each absorb spend creates a new singleton coin, resetting the coin's confirmed height and thus the `ASSERT_HEIGHT_RELATIVE` condition enforced by the waiting-room CLVM puzzle. This indefinitely prevents the farmer from completing their pool exit as long as farming rewards continue to appear at the `p2_singleton_puzzle_hash`.

---

### Finding Description

When a farmer initiates a pool exit, the singleton transitions to `LEAVING_POOL` state. The waiting-room inner puzzle (`POOL_WAITINGROOM_INNERPUZ`) enforces a `relative_lock_height` via `ASSERT_HEIGHT_RELATIVE`, meaning the exit spend is only valid once `current_height >= coin_confirmed_height + relative_lock_height`.

The absorb spend path (`create_absorb_spend`) is **completely permissionless** — it requires no owner signature and zero fee: [1](#0-0) 

```python
claim_spend = WalletSpendBundle(all_spends, G2Element())
# If fee is 0, no signatures are required to absorb
if fee > 0:
    await self.generate_fee_transaction(...)
```

The absorb spend is valid while the singleton is in `LEAVING_POOL` (waiting-room) state: [2](#0-1) 

```python
elif is_pool_waitingroom_inner_puzzle(inner_puzzle):
    # inner sol is (spend_type, destination_puzhash, pool_reward_amount, pool_reward_height, extra_data)
    inner_sol = Program.to([0, reward_amount, height])
```

Each absorb spend **spends the current singleton coin and creates a new one**, giving the new coin a fresh `confirmed_height`. This resets the `ASSERT_HEIGHT_RELATIVE` clock.

At the wallet layer, `new_peak` computes the leave height from `tip_height`, which is the height of the most recent singleton spend (including absorb spends): [3](#0-2) 

```python
if (
    self.target_state.state in {FARMING_TO_POOL.value, SELF_POOLING.value}
    and pool_wallet_info.current.state == LEAVING_POOL.value
):
    leave_height = tip_height + pool_wallet_info.current.relative_lock_height
    # Add some buffer (+2) to reduce chances of a reorg
    if peak_height > leave_height + 2:
```

`tip_height` is updated by `apply_state_transition` every time a new singleton spend (including absorb) is recorded: [4](#0-3) 

```python
await self.wallet_state_manager.pool_store.add_spend(self.wallet_id, new_state, block_height)
tip_spend = (await self.get_tip())[1]
```

The absorb spend requires a valid farming reward coin at the `p2_singleton_puzzle_hash`. These coins are created automatically whenever the farmer farms a block. The attacker only needs to monitor the chain and submit the absorb bundle (no signature, no fee) before the farmer completes their exit.

---

### Impact Explanation

**High — Permanent or long-lived inability for a farmer to complete pool exit (pool action).**

An attacker who monitors the chain can:
1. Observe the farmer's singleton enter `LEAVING_POOL` state at height H (singleton coin C1 created)
2. Wait for the farmer to farm a block, creating a reward at `p2_singleton_puzzle_hash`
3. Submit a permissionless absorb spend bundle (no signature, no fee) creating new singleton coin C2 at height H+k
4. The `ASSERT_HEIGHT_RELATIVE` clock resets: exit now requires height H+k+`relative_lock_height`
5. Repeat for every new farming reward

As long as the farmer continues farming (normal operation), new rewards appear and the attacker can keep resetting the timer. The farmer is forced to choose between: (a) stop farming entirely (losing all rewards) or (b) remain permanently trapped in `LEAVING_POOL` state. The `relative_lock_height` ranges from 5 to 1000 blocks per the wallet constants: [5](#0-4) 

```python
MINIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 5
MAXIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 1000
```

---

### Likelihood Explanation

**Medium.** The attacker must:
- Know the victim's `p2_singleton_puzzle_hash` (fully public, derivable from `launcher_id`)
- Monitor the chain for new farming rewards at that address
- Submit absorb spend bundles with zero fee and no signature

All of these are trivially achievable by any unprivileged network participant. The only constraint is that farming rewards must exist, which is the normal operating condition for any active farmer.

---

### Recommendation

The waiting-room inner puzzle (`POOL_WAITINGROOM_INNERPUZ`) should require the owner's signature for the absorb path when the singleton is in `LEAVING_POOL` state, or the absorb path should be disabled entirely while in `LEAVING_POOL` state. Alternatively, the `ASSERT_HEIGHT_RELATIVE` condition for the exit should be anchored to the height at which the singleton first entered `LEAVING_POOL` state (stored in the puzzle or solution), rather than the height of the most recent singleton coin.

---

### Proof of Concept

1. Farmer's singleton enters `LEAVING_POOL` at block 1000 with `relative_lock_height = 100`. Singleton coin C1 is created at height 1000. Exit requires height ≥ 1100.
2. Farmer farms a block at height 1050, creating reward coin R1 at `p2_singleton_puzzle_hash`.
3. Attacker calls `create_absorb_spend(last_coin_spend=C1_spend, current_state=LEAVING_POOL_state, ...)` and submits the bundle with `G2Element()` (empty signature). This is accepted on-chain at height 1051, creating new singleton coin C2.
4. `ASSERT_HEIGHT_RELATIVE` now requires height ≥ 1051 + 100 = 1151.
5. Farmer farms again at height 1100, creating R2. Attacker absorbs again at 1101, creating C3. Exit now requires ≥ 1201.
6. This repeats indefinitely. The farmer can never reach the required height while the attacker keeps absorbing.

The absorb spend bundle construction is confirmed permissionless in `create_absorb_spend`: [6](#0-5) 

and the waiting-room absorb path is confirmed valid by the lifecycle test: [7](#0-6)

### Citations

**File:** chia/pools/pool_wallet.py (L69-70)
```python
    MINIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 5
    MAXIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 1000
```

**File:** chia/pools/pool_wallet.py (L286-288)
```python
        await self.wallet_state_manager.pool_store.add_spend(self.wallet_id, new_state, block_height)
        tip_spend = (await self.get_tip())[1]
        self.log.info(f"New PoolWallet singleton tip_coin: {tip_spend} farmed at height {block_height}")
```

**File:** chia/pools/pool_wallet.py (L780-783)
```python
        claim_spend = WalletSpendBundle(all_spends, G2Element())

        # If fee is 0, no signatures are required to absorb
        if fee > 0:
```

**File:** chia/pools/pool_wallet.py (L819-826)
```python
        if (
            self.target_state.state in {FARMING_TO_POOL.value, SELF_POOLING.value}
            and pool_wallet_info.current.state == LEAVING_POOL.value
        ):
            leave_height = tip_height + pool_wallet_info.current.relative_lock_height

            # Add some buffer (+2) to reduce chances of a reorg
            if peak_height > leave_height + 2:
```

**File:** chia/pools/pool_puzzles.py (L252-307)
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
