### Title
Pool Operator Can Permanently Reset `LEAVING_POOL` Lock Timer via Permissionless Absorb Spends - (`File: chia/pools/pool_puzzles.py`, `chia/pools/pool_wallet.py`)

### Summary
The Chia pool singleton protocol allows a pool operator to perform "absorb" spends on a farmer's singleton even while it is in the `LEAVING_POOL` (waiting room) state, without requiring the farmer's signature. Each absorb spend creates a new singleton coin at the current block height, which resets the `ASSERT_HEIGHT_RELATIVE` lock enforced by `POOL_WAITINGROOM_INNERPUZ`. A malicious pool can repeat this indefinitely, permanently preventing the farmer from completing their exit and continuing to receive all farming rewards.

### Finding Description

The Chia pool protocol uses a two-step exit: the farmer first transitions the singleton to `LEAVING_POOL` (the waiting room state), then after `relative_lock_height` blocks, submits a second spend to complete the exit. The waiting room inner puzzle (`POOL_WAITINGROOM_INNERPUZ`) enforces `ASSERT_HEIGHT_RELATIVE(relative_lock_height)` on the exit spend, measured relative to the **creation height of the current singleton coin**.

The waiting room puzzle supports two spend paths:
- **Absorb path** (`spend_type = 0`): Claims a `p2_singleton` farming reward, recreates the singleton at the same state, no owner signature required.
- **Escape path** (`spend_type = 1`): Transitions to the next state, requires owner signature.

In `create_absorb_spend`, the waiting room absorb path is explicitly supported:

```python
elif is_pool_waitingroom_inner_puzzle(inner_puzzle):
    inner_sol = Program.to([0, reward_amount, height])
```

The resulting spend bundle uses `G2Element()` (empty/no signature). The pool can construct and submit this spend unilaterally whenever a `p2_singleton` reward coin exists at the farmer's `p2_singleton_puzzle_hash`.

Each absorb spend destroys the current singleton coin and creates a new one at the current block height. The `ASSERT_HEIGHT_RELATIVE` condition in the subsequent exit spend is then measured from this new creation height, effectively resetting the lock timer.

The wallet-side check in `self_pool()` and `join_pool()` also uses `history[-1][0]` (the height of the most recent singleton spend) as the reference point:

```python
last_height: uint32 = history[-1][0]
if (
    await self.wallet_state_manager.blockchain.get_finished_sync_up_to()
    <= last_height + current_state.current.relative_lock_height
):
    raise ValueError(...)
```

And `new_peak()` similarly computes:

```python
leave_height = tip_height + pool_wallet_info.current.relative_lock_height
```

Both the on-chain CLVM enforcement and the wallet-side guard are reset by each absorb spend.

### Impact Explanation

A malicious pool can permanently trap a farmer in `LEAVING_POOL` state. The farmer's plots continue to farm to the `p2_singleton_puzzle_hash`, and all block rewards continue flowing to the pool's `target_puzzle_hash`. The farmer cannot redirect rewards to self-pooling or another pool. This constitutes unauthorized payout redirection and permanent singleton state lock — a High-severity impact under the allowed scope.

### Likelihood Explanation

The pool operator is a semi-trusted party with knowledge of the farmer's `p2_singleton_puzzle_hash` and the singleton's current state (both are public on-chain). The pool needs only one valid `p2_singleton` reward coin to perform each absorb spend. As long as the farmer's plots are active, reward coins are continuously generated, giving the pool an unlimited supply of reset opportunities. No leaked keys, admin access, or cryptographic breaks are required.

### Recommendation

1. **Disallow absorb spends in `LEAVING_POOL` state at the CLVM level**: The `POOL_WAITINGROOM_INNERPUZ` should reject the absorb path (`spend_type = 0`) entirely, or redirect absorbed rewards to the farmer's `target_puzzle_hash` without recreating the singleton (i.e., use a separate coin spend that does not touch the singleton).

2. **Anchor the lock timer to the first `LEAVING_POOL` spend**: Record the block height at which the singleton first entered `LEAVING_POOL` state (e.g., in the puzzle or solution memo) and enforce `ASSERT_HEIGHT_ABSOLUTE(entry_height + relative_lock_height)` instead of `ASSERT_HEIGHT_RELATIVE`, so subsequent absorb spends cannot reset the reference point.

3. **Wallet-side mitigation**: In `self_pool()` and `join_pool()`, use the height of the spend that first set `state == LEAVING_POOL` rather than `history[-1][0]`, so absorb spends do not affect the wallet's own timer check.

### Proof of Concept

1. Farmer joins pool with `relative_lock_height = 32`. Singleton is in `FARMING_TO_POOL` state.
2. Farmer calls `pw_self_pool()`. Singleton transitions to `LEAVING_POOL` at block height H. Farmer must wait until block H + 32.
3. At block H + 30 (2 blocks before exit), the pool constructs an absorb spend using `create_absorb_spend(last_coin_spend, current_state, launcher_coin, height=H+30, ...)` with `inner_sol = Program.to([0, reward_amount, H+30])` and submits it with `G2Element()` (no signature needed).
4. The absorb spend is accepted on-chain. A new singleton coin is created at block H + 30. The old singleton coin is spent.
5. The farmer's exit spend now fails: `ASSERT_HEIGHT_RELATIVE(32)` requires the current block to be ≥ (H + 30) + 32 = H + 62.
6. The pool repeats step 3 every 30 blocks. The farmer can never satisfy `ASSERT_HEIGHT_RELATIVE(32)`.
7. All farming rewards continue to flow to the pool's `target_puzzle_hash` indefinitely.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** chia/pools/pool_puzzles.py (L265-271)
```python
    if is_pool_member_inner_puzzle(inner_puzzle):
        # inner sol is (spend_type, pool_reward_amount, pool_reward_height, extra_data)
        inner_sol: Program = Program.to([reward_amount, height])
    elif is_pool_waitingroom_inner_puzzle(inner_puzzle):
        # inner sol is (spend_type, destination_puzhash, pool_reward_amount, pool_reward_height, extra_data)
        inner_sol = Program.to([0, reward_amount, height])
    else:
```

**File:** chia/pools/pool_puzzles.py (L290-308)
```python
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

**File:** chia/pools/pool_wallet.py (L693-703)
```python
        if current_state.current.state == LEAVING_POOL.value:
            total_fee = fee
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

**File:** chia/pools/pool_wallet.py (L780-782)
```python
        claim_spend = WalletSpendBundle(all_spends, G2Element())

        # If fee is 0, no signatures are required to absorb
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
