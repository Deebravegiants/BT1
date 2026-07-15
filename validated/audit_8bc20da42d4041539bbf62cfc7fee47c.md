### Title
Permissionless Absorb Spend Resets Pool Exit Countdown, Enabling Indefinite DOS of Farmer's Pool Withdrawal — (`chia/pools/pool_puzzles.py`, `chia/pools/pool_wallet.py`)

---

### Summary

The pool singleton's absorb-reward spend path requires **no signature** and can be submitted by any unprivileged party. When a farmer is in `LEAVING_POOL` state, an attacker (including the pool operator itself) can repeatedly trigger absorb spends just before the `relative_lock_height` countdown expires. Each absorb creates a new singleton coin at the current block height, resetting the on-chain `ASSERT_HEIGHT_RELATIVE` countdown. The farmer is permanently prevented from completing their pool exit, and farming rewards continue flowing to the pool's address.

---

### Finding Description

**Permissionless absorb path — no signature required**

`create_absorb_spend()` in `chia/pools/pool_puzzles.py` constructs a spend bundle that is submitted with an empty `G2Element()` signature: [1](#0-0) 

The wallet confirms this explicitly: [2](#0-1) 

The absorb spend is valid for both `FARMING_TO_POOL` and `LEAVING_POOL` (waiting room) states: [3](#0-2) 

**Absorb while in LEAVING_POOL resets the countdown**

When a farmer initiates a pool exit, the singleton transitions to `LEAVING_POOL` state. The farmer must wait `relative_lock_height` blocks (up to 1000, enforced on-chain via `ASSERT_HEIGHT_RELATIVE`) before submitting the second travel transaction. The wallet computes the leave height from the **tip singleton spend height**: [4](#0-3) 

`tip_height` is the block height of the most recent singleton spend, stored via `apply_state_transition()`: [5](#0-4) 

An absorb spend **spends the current singleton coin and creates a new one** at the current block height. The new singleton coin's age starts at zero. The on-chain `ASSERT_HEIGHT_RELATIVE` condition in `pool_waiting_room_innerpuz` applies to the coin being spent — after an absorb, the new singleton coin must age `relative_lock_height` blocks before the exit can proceed. The test suite confirms this reset behavior: [6](#0-5) 

**Attack path**

1. Farmer submits the first travel transaction, entering `LEAVING_POOL` state at block `M`.
2. Farmer farms a block; a reward coin appears at the deterministic `p2_singleton_puzzle_hash`.
3. Attacker (pool operator or any third party) submits an absorb spend bundle (no signature needed) at block `M + relative_lock_height − 1`, just before the countdown expires.
4. A new singleton coin is created at block `M + relative_lock_height − 1`. The countdown resets: the farmer must now wait until block `M + 2·relative_lock_height − 1`.
5. Repeat from step 2 indefinitely.

The `p2_singleton_puzzle_hash` is public and deterministic: [7](#0-6) 

Farming reward coins appear at this address automatically whenever the farmer farms a block, providing the attacker with a continuous supply of absorb opportunities.

---

### Impact Explanation

**High — Permanent or long-lived inability for honest farmers to complete pool exit.**

- The farmer cannot complete the `LEAVING_POOL → SELF_POOLING` (or `→ FARMING_TO_POOL`) transition.
- All farming rewards continue to be directed to the pool's `target_puzzle_hash` for the duration of the attack.
- The pool operator is the most motivated attacker: it can monitor the chain and submit absorb spends at zero cost (no fee required) to hold farmers hostage indefinitely.
- The `MAXIMUM_RELATIVE_LOCK_HEIGHT` of 1000 blocks means each absorb buys the attacker ~1000 blocks (~6–7 hours on mainnet) of continued pool control over the farmer's rewards. [8](#0-7) 

---

### Likelihood Explanation

The pool operator has direct financial incentive to prevent farmers from leaving (retaining farming rewards). The attack requires only:
- Knowledge of the farmer's `launcher_id` (public, on-chain).
- A farming reward coin to exist at `p2_singleton_puzzle_hash` (occurs naturally whenever the farmer farms a block).
- Submission of a zero-signature spend bundle.

No keys, admin access, or cryptographic breaks are required. The pool already monitors the blockchain for reward coins as part of normal operations.

---

### Recommendation

The `pool_waiting_room_innerpuz` should enforce that the `ASSERT_HEIGHT_RELATIVE` countdown is measured from the **travel spend** (the spend that entered `LEAVING_POOL`), not from the most recent singleton spend. One approach: record the entry block height in the singleton's state and use `ASSERT_HEIGHT_ABSOLUTE` instead of `ASSERT_HEIGHT_RELATIVE`, so that absorb spends during the waiting period do not reset the exit deadline. Alternatively, the waiting room puzzle should reject absorb spends entirely while in `LEAVING_POOL` state, directing any unclaimed rewards to be absorbed only after the exit is complete.

---

### Proof of Concept

```
Block M:   Farmer submits travel spend → singleton enters LEAVING_POOL
           relative_lock_height = 1000 blocks
           leave_height = M + 1000

Block M+1: Farmer farms a block → reward coin appears at p2_singleton_puzzle_hash

Block M+999: Attacker submits absorb spend (G2Element() signature, no key needed):
             SpendBundle([singleton_coinsol, reward_coinsol], G2Element())
             → New singleton coin created at block M+999
             → leave_height resets to (M+999) + 1000 = M+1999

Block M+1000: Farmer farms another block → new reward coin appears

Block M+1998: Attacker submits another absorb spend
              → leave_height resets to M+2998

... (repeats indefinitely)
```

The farmer's exit is permanently blocked. All farming rewards continue to flow to the pool's `target_puzzle_hash` for the duration of the attack. [9](#0-8) [10](#0-9)

### Citations

**File:** chia/pools/pool_puzzles.py (L120-121)
```python
def launcher_id_to_p2_puzzle_hash(launcher_id: bytes32, seconds_delay: uint64, delayed_puzzle_hash: bytes32) -> bytes32:
    return create_p2_singleton_puzzle_hash(SINGLETON_MOD_HASH, launcher_id, seconds_delay, delayed_puzzle_hash)
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

**File:** chia/pools/pool_wallet.py (L68-71)
```python
    MINIMUM_INITIAL_BALANCE: ClassVar[int] = 1
    MINIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 5
    MAXIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 1000
    DEFAULT_MAX_CLAIM_SPENDS: ClassVar[int] = 100
```

**File:** chia/pools/pool_wallet.py (L286-288)
```python
        await self.wallet_state_manager.pool_store.add_spend(self.wallet_id, new_state, block_height)
        tip_spend = (await self.get_tip())[1]
        self.log.info(f"New PoolWallet singleton tip_coin: {tip_spend} farmed at height {block_height}")
```

**File:** chia/pools/pool_wallet.py (L780-780)
```python
        claim_spend = WalletSpendBundle(all_spends, G2Element())
```

**File:** chia/pools/pool_wallet.py (L782-782)
```python
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
