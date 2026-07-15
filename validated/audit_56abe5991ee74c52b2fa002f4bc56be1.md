### Title
Pool Singleton `relative_lock_height` Countdown Reset by Permissionless Absorb Spend While in `LEAVING_POOL` State — (`File: chia/pools/pool_puzzles.py`)

---

### Summary

When a farmer initiates leaving a pool (entering `LEAVING_POOL` / waiting-room state), the on-chain `ASSERT_HEIGHT_RELATIVE` countdown begins from the block height at which the singleton coin was created. Any absorb spend executed while in this state creates a **new** singleton coin, resetting the countdown reference height. Because absorb spends are permissionless, a pool operator can continuously absorb pending farming rewards to prevent the farmer from ever completing the exit.

---

### Finding Description

The pool singleton's waiting-room puzzle enforces `ASSERT_HEIGHT_RELATIVE(relative_lock_height)`, which requires the coin to be spent at least `relative_lock_height` blocks after **its own creation**. This is a per-coin, not per-state-transition, measurement.

`create_absorb_spend` in `chia/pools/pool_puzzles.py` handles the waiting-room case by spending the current singleton coin and creating a new one:

```python
elif is_pool_waitingroom_inner_puzzle(inner_puzzle):
    inner_sol = Program.to([0, reward_amount, height])
``` [1](#0-0) 

This spend consumes the existing singleton coin and produces a new singleton coin whose creation height is the absorb block height. The `ASSERT_HEIGHT_RELATIVE` condition on the **new** coin is therefore measured from the absorb height, not from the original `LEAVING_POOL` transition height.

The wallet-side guard in `self_pool` compounds this: it reads `history[-1][0]` (the height of the most recent spend in the pool store) to determine when the lock expires:

```python
history: list[tuple[uint32, CoinSpend]] = await self.get_spend_history()
last_height: uint32 = history[-1][0]
if (
    await self.wallet_state_manager.blockchain.get_finished_sync_up_to()
    <= last_height + current_state.current.relative_lock_height
):
    raise ValueError(...)
``` [2](#0-1) 

`apply_state_transition` records every singleton spend — including absorb spends — into the pool store:

```python
await self.wallet_state_manager.pool_store.add_spend(self.wallet_id, new_state, block_height)
``` [3](#0-2) 

So after an absorb at height H+N, `history[-1][0]` becomes H+N, and the wallet will not allow the farmer to complete the exit until height H+N+`relative_lock_height`.

---

### Impact Explanation

A pool operator can submit absorb spends permissionlessly (no signature required when `fee == 0`):

```python
# If fee is 0, no signatures are required to absorb
if fee > 0:
    await self.generate_fee_transaction(...)
``` [4](#0-3) 

As long as the farmer continues farming and generating `p2_singleton` reward coins, the pool operator can absorb them just before the countdown expires, resetting it each time. This constitutes a **permanent, long-lived inability for an honest farmer to complete a valid pool exit action** — matching the High impact category.

---

### Likelihood Explanation

The attack requires only that:
1. The farmer is actively farming (generating new `p2_singleton` reward coins).
2. The pool operator monitors the chain and submits absorb spends before the countdown expires.

Both conditions are trivially satisfied for any active pool operator with a financial incentive to retain farmers. The absorb spend requires no key material from the farmer.

---

### Recommendation

The `ASSERT_HEIGHT_RELATIVE` countdown should be anchored to the block height of the `LEAVING_POOL` state transition, not to the most recently created singleton coin. One approach is to store the exit-initiation height in the waiting-room puzzle state and use `ASSERT_HEIGHT_ABSOLUTE(exit_height + relative_lock_height)` instead of `ASSERT_HEIGHT_RELATIVE`. Alternatively, absorb spends should be disallowed (or made a no-op for the countdown) while the singleton is in `LEAVING_POOL` state.

---

### Proof of Concept

1. Farmer calls `pw_self_pool` at block H. Singleton transitions to `LEAVING_POOL` with `relative_lock_height = R`. New singleton coin created at height H.
2. Pool operator watches the chain. At block H+R-1 (one block before the lock expires), a farming reward coin exists at the `p2_singleton_puzzle_hash`.
3. Pool operator calls `create_absorb_spend` against the waiting-room singleton. This is accepted with no signature (`fee=0`). A new singleton coin is created at height H+R-1.
4. The `ASSERT_HEIGHT_RELATIVE(R)` on the new coin now requires height ≥ H+R-1+R = H+2R-1 before exit.
5. Pool operator repeats step 2–4 indefinitely. The farmer can never exit as long as farming rewards keep arriving.

The test in `test_pool_puzzles_lifecycle.py` confirms absorb succeeds while in the waiting room (height 3, `relative_lock_height=5000`), and the exit only succeeds at height 10000 (> 3+5000), demonstrating the countdown is measured from the absorb coin's creation height. [5](#0-4)

### Citations

**File:** chia/pools/pool_puzzles.py (L268-270)
```python
    elif is_pool_waitingroom_inner_puzzle(inner_puzzle):
        # inner sol is (spend_type, destination_puzhash, pool_reward_amount, pool_reward_height, extra_data)
        inner_sol = Program.to([0, reward_amount, height])
```

**File:** chia/pools/pool_wallet.py (L286-286)
```python
        await self.wallet_state_manager.pool_store.add_spend(self.wallet_id, new_state, block_height)
```

**File:** chia/pools/pool_wallet.py (L695-703)
```python
            history: list[tuple[uint32, CoinSpend]] = await self.get_spend_history()
            last_height: uint32 = history[-1][0]
            if (
                await self.wallet_state_manager.blockchain.get_finished_sync_up_to()
                <= last_height + current_state.current.relative_lock_height
            ):
                raise ValueError(
                    f"Cannot self pool until height {last_height + current_state.current.relative_lock_height}"
                )
```

**File:** chia/pools/pool_wallet.py (L782-784)
```python
        # If fee is 0, no signatures are required to absorb
        if fee > 0:
            await self.generate_fee_transaction(
```

**File:** chia/_tests/pools/test_pool_puzzles_lifecycle.py (L335-385)
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

        # LEAVE THE WAITING ROOM
        time = CoinTimestamp(20000000, 10000)
        # find the singleton
        singleton_coinsol: CoinSpend = next(
            filter(
                lambda e: e.coin.amount == START_AMOUNT,
                coin_sols,
            )
        )
        singleton: Coin = get_most_recent_singleton_coin_from_coin_spend(singleton_coinsol)
        # get the relevant coin solution
        return_coinsol, _ = create_travel_spend(
            singleton_coinsol,
            launcher_coin,
            target_pool_state,
            pool_state,
            GENESIS_CHALLENGE,
            DELAY_TIME,
            DELAY_PH,
        )
        # Test that we can retrieve the extra data
        assert solution_to_pool_state(return_coinsol) == pool_state
        # sign the serialized target state
        data = Program.to([pooling_innerpuz.get_tree_hash(), START_AMOUNT, bytes(pool_state)]).get_tree_hash()
        sig: G2Element = AugSchemeMPL.sign(
            sk,
            (data + singleton.name() + DEFAULT_CONSTANTS.AGG_SIG_ME_ADDITIONAL_DATA),
        )
        # Spend it!
        coin_db.update_coin_store_for_spend_bundle(
            SpendBundle([return_coinsol], sig), time, DEFAULT_CONSTANTS.MAX_BLOCK_COST_CLVM
        )
```
