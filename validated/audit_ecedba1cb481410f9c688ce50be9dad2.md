### Title
Permissionless Pool Reward Absorb Resets Singleton Coin Height, Enabling Indefinite DoS on Pool Exit — (File: `chia/pools/pool_puzzles.py`, `chia/pools/pool_wallet.py`)

### Summary

The pool singleton's absorb-reward spend path requires no signature when `fee=0`. Any unprivileged actor who observes a farming reward at a farmer's `p2_singleton` puzzle hash can construct and submit a valid absorb spend bundle. Each absorb creates a new singleton coin, resetting the coin's confirmed block height. Because the waiting-room exit condition is `ASSERT_HEIGHT_RELATIVE relative_lock_height` — measured from the **current singleton coin's** confirmed height — an attacker who repeatedly absorbs rewards can keep resetting that counter, permanently preventing the farmer from satisfying the height lock and leaving the pool.

### Finding Description

**Permissionless absorb path (no signature required)**

`create_absorb_spend` in `chia/pools/pool_puzzles.py` builds a spend bundle that spends the singleton coin and the farming-reward `p2_singleton` coin. The pool wallet assembles this bundle with an empty aggregate signature:

```python
claim_spend = WalletSpendBundle(all_spends, G2Element())
# If fee is 0, no signatures are required to absorb
``` [1](#0-0) 

All inputs needed to construct the absorb spend — the last singleton coin spend, pool state, launcher coin, reward height, genesis challenge, delay parameters — are fully public on-chain. An attacker can reconstruct them without any privileged access.

**Height lock is relative to the singleton coin's creation height**

The waiting-room inner puzzle is curried with `relative_lock_height`:

```python
return POOL_WAITING_ROOM_MOD.curry(
    target_puzzle_hash, p2_singleton_puzzle_hash, bytes(owner_pubkey),
    pool_reward_prefix, relative_lock_height
)
``` [2](#0-1) 

The exit spend from the waiting room must satisfy `ASSERT_HEIGHT_RELATIVE relative_lock_height`. In Chia's consensus, this condition is evaluated against the **coin being spent** — the singleton coin. Every absorb spend destroys the current singleton coin and creates a new one at the current block height, resetting the relative-height counter to zero.

**Absorb spend creates a new singleton coin**

`create_absorb_spend` returns two `CoinSpend` objects: one spending the current singleton and one spending the reward coin. The singleton spend produces a new singleton coin whose `confirmed_block_index` is the block in which the absorb is included. [3](#0-2) 

### Impact Explanation

A farmer in `LEAVING_POOL` state must wait `relative_lock_height` blocks (up to 1000, ≈14.4 hours) before the exit spend is valid. Each time the attacker absorbs a farming reward, the singleton coin is replaced and the counter resets. As long as the farmer continues farming (generating rewards at the `p2_singleton` puzzle hash), the attacker can keep absorbing them and the farmer can never satisfy the height lock. This is a permanent, low-cost DoS on pool exit — a protected singleton state transition — with no on-chain defense.

Impact category: **High — Permanent or long-lived inability for honest farmers to process valid pool actions (pool exit / singleton state transition) under normal network assumptions.**

### Likelihood Explanation

- The absorb spend is fully permissionless at `fee=0` and all required data is public.
- The attacker's only cost is the transaction fee (zero at `fee=0`) and the ability to monitor the chain for farming rewards at the target `p2_singleton` puzzle hash.
- The `p2_singleton` puzzle hash is deterministic and publicly derivable from the launcher ID.
- The farmer cannot avoid generating rewards at that puzzle hash while their plots are still configured for the pool.
- `MINIMUM_RELATIVE_LOCK_HEIGHT = 5` and `MAXIMUM_RELATIVE_LOCK_HEIGHT = 1000` are enforced by the wallet, but the CLVM puzzle itself does not prevent absorb spends from resetting the counter. [4](#0-3) 

### Recommendation

**Short term:** In the waiting-room inner puzzle (`POOL_WAITINGROOM_INNERPUZ`), track the block height at which the farmer first entered the waiting room (e.g., store it in the singleton's state) and enforce `ASSERT_HEIGHT_ABSOLUTE (entry_height + relative_lock_height)` instead of `ASSERT_HEIGHT_RELATIVE`. This makes the exit deadline absolute and immune to absorb-induced resets.

**Long term:** Add an invariant test that verifies a farmer in `LEAVING_POOL` state can always exit within `relative_lock_height` blocks regardless of how many absorb spends occur during that window.

### Proof of Concept

1. Farmer calls `pw_self_pool` to enter `LEAVING_POOL` state at block height `H`. The singleton coin is confirmed at height `H`.
2. Farmer's plots farm a block at height `H + K` (where `K < relative_lock_height`), creating a farming reward coin at the `p2_singleton` puzzle hash.
3. Attacker reads the public blockchain state, reconstructs the absorb spend using `create_absorb_spend(last_coin_spend, current_state, launcher_coin, K, genesis_challenge, delay_time, delay_ph)`, and submits `WalletSpendBundle(absorb_spends, G2Element())` with zero fee.
4. The absorb is accepted (no signature required). A new singleton coin is created at height `H + K`.
5. The farmer's exit spend (built against the old singleton coin at height `H`) is now invalid — that coin is spent.
6. The farmer rebuilds the exit spend against the new singleton coin. It fails with `ASSERT_HEIGHT_RELATIVE_FAILED` because the new coin is only 0 blocks old.
7. Attacker repeats from step 2 every time a new farming reward appears. The farmer can never accumulate `relative_lock_height` blocks on any single singleton coin. [5](#0-4) [1](#0-0) [6](#0-5)

### Citations

**File:** chia/pools/pool_wallet.py (L68-70)
```python
    MINIMUM_INITIAL_BALANCE: ClassVar[int] = 1
    MINIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 5
    MAXIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 1000
```

**File:** chia/pools/pool_wallet.py (L780-782)
```python
        claim_spend = WalletSpendBundle(all_spends, G2Element())

        # If fee is 0, no signatures are required to absorb
```

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
