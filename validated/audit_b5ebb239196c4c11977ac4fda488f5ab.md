### Title
Pool Singleton `relative_lock_height` Minimum Not Enforced at CLVM Level, Enabling Immediate Pool Exit and Reward Diversion — (`File: chia/pools/pool_wallet.py`)

### Summary

The `relative_lock_height` parameter embedded in pool singleton CLVM puzzles is only validated at the wallet software layer (`_verify_pooling_state`), not at the consensus/CLVM layer. An unprivileged farmer can craft a spend bundle directly — bypassing the wallet RPC — to create a pool singleton with `relative_lock_height = 0`. Because the waiting room puzzle emits `ASSERT_HEIGHT_RELATIVE relative_lock_height`, a value of 0 is always satisfied, allowing the farmer to exit the pool in the very next block after declaring intent to leave, stealing block rewards that should have gone to the pool.

### Finding Description

`PoolWallet` defines `MINIMUM_RELATIVE_LOCK_HEIGHT = 5` and enforces it in `_verify_pooling_state`: [1](#0-0) [2](#0-1) 

`_verify_initial_target_state` calls this and raises `ValueError` if the check fails: [3](#0-2) 

This guard is applied when creating a new pool wallet transaction: [4](#0-3) 

And when joining a pool: [5](#0-4) 

However, this validation exists **only in the Python wallet layer**. The CLVM waiting room puzzle is curried with whatever `relative_lock_height` value is provided: [6](#0-5) 

The consensus layer has no knowledge of `MINIMUM_RELATIVE_LOCK_HEIGHT`. An attacker who constructs and submits a spend bundle directly (bypassing the wallet RPC) can create a pool singleton with `relative_lock_height = 0`. The resulting waiting room puzzle emits `ASSERT_HEIGHT_RELATIVE 0`, which is always satisfied — a coin is always at least 0 blocks old relative to its confirmation height.

The CLI path also only checks the upper bound (`> 1000`), not the lower bound: [7](#0-6) 

### Impact Explanation

The `relative_lock_height` is the sole on-chain security mechanism preventing a farmer from cheating a pool. The protocol comment makes this explicit: [8](#0-7) 

With `relative_lock_height = 0`:

1. **Block N**: Farmer wins a block reward → `p2_singleton` coin is created; farmer simultaneously submits FARMING_TO_POOL → LEAVING_POOL singleton transition.
2. **Block N+1**: Farmer immediately submits LEAVING_POOL → SELF_POOLING transition (since `ASSERT_HEIGHT_RELATIVE 0` is always satisfied). In the same block, farmer spends the `p2_singleton` coin to their own address.

The pool has no opportunity to claim the `p2_singleton` reward between blocks N and N+1. With the standard `relative_lock_height ≥ 5`, the pool has at least 5 blocks to react and claim the reward first.

This constitutes **unauthorized pool reward diversion** — a High/Critical impact under the allowed scope.

### Likelihood Explanation

- Any farmer can craft a raw spend bundle without using the wallet RPC.
- The blockchain/mempool accepts the spend bundle because the CLVM puzzle is valid; no consensus rule rejects `relative_lock_height = 0`.
- The pool operator cannot prevent this at the protocol level; pool-side checks on `relative_lock_height` are advisory only.
- The attack requires the farmer to win at least one block reward while farming for the pool, which is a normal farming event.

### Recommendation

Enforce a hard minimum `relative_lock_height` inside the CLVM waiting room puzzle itself, not just in the Python wallet layer. The puzzle should assert that the curried `relative_lock_height` is at least some protocol-defined constant (e.g., 5) before emitting the `ASSERT_HEIGHT_RELATIVE` condition. Alternatively, the consensus layer should reject pool singleton spends where the curried `relative_lock_height` is below the protocol minimum.

At the Python layer, the error message in `_verify_pooling_state` currently says "recommended minimum," which understates the security significance: [9](#0-8) 

This should be treated as a hard protocol requirement, not a recommendation.

### Proof of Concept

1. Construct a launcher spend and waiting room inner puzzle with `relative_lock_height = 0` using `create_waiting_room_inner_puzzle` directly (bypassing `_verify_initial_target_state`): [6](#0-5) 

2. Submit the spend bundle directly to the full node mempool. The blockchain accepts it because the CLVM execution is valid.

3. Join a pool (or simulate one). Win a block reward — the `p2_singleton` coin is created.

4. In the same block as the reward, submit FARMING_TO_POOL → LEAVING_POOL singleton transition.

5. In the next block, submit LEAVING_POOL → SELF_POOLING transition. `ASSERT_HEIGHT_RELATIVE 0` is always satisfied (confirmed by consensus test behavior: `ASSERT_HEIGHT_RELATIVE 0` → `None` error, i.e., always passes).

6. In the same block, spend the `p2_singleton` coin to the farmer's own address, diverting the pool reward.

The pool has no on-chain recourse because the `relative_lock_height = 0` singleton is a valid CLVM object accepted by consensus.

### Citations

**File:** chia/pools/pool_wallet.py (L68-70)
```python
    MINIMUM_INITIAL_BALANCE: ClassVar[int] = 1
    MINIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 5
    MAXIMUM_RELATIVE_LOCK_HEIGHT: ClassVar[int] = 1000
```

**File:** chia/pools/pool_wallet.py (L97-103)
```python
    The pool is also protected, by not allowing members to cheat by quickly leaving a pool,
    and claiming a block that was pledged to the pool.

    The pooling protocol and smart coin prevents a user from quickly leaving a pool
    by enforcing a wait time when leaving the pool. A minimum number of blocks must pass
    after the user declares that they are leaving the pool, and before they can start to
    self-claim rewards again.
```

**File:** chia/pools/pool_wallet.py (L145-161)
```python
    @classmethod
    def _verify_pooling_state(cls, state: PoolState) -> str | None:
        err = ""
        if state.relative_lock_height < cls.MINIMUM_RELATIVE_LOCK_HEIGHT:
            err += (
                f" Pool relative_lock_height ({state.relative_lock_height})"
                f"is less than recommended minimum ({cls.MINIMUM_RELATIVE_LOCK_HEIGHT})"
            )
        elif state.relative_lock_height > cls.MAXIMUM_RELATIVE_LOCK_HEIGHT:
            err += (
                f" Pool relative_lock_height ({state.relative_lock_height})"
                f"is greater than recommended maximum ({cls.MAXIMUM_RELATIVE_LOCK_HEIGHT})"
            )

        if state.pool_url in {None, ""}:
            err += " Empty pool url in pooling state"
        return err
```

**File:** chia/pools/pool_wallet.py (L182-186)
```python
    @classmethod
    def _verify_initial_target_state(cls, initial_target_state: PoolState) -> None:
        err = cls._verify_pool_state(initial_target_state)
        if err:
            raise ValueError(f"Invalid internal Pool State: {err}: {initial_target_state}")
```

**File:** chia/pools/pool_wallet.py (L424-425)
```python
        # Verify Parameters - raise if invalid
        PoolWallet._verify_initial_target_state(initial_target_state)
```

**File:** chia/pools/pool_wallet.py (L656-656)
```python
        PoolWallet._verify_initial_target_state(target_state)
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

**File:** chia/cmds/plotnft_funcs.py (L67-68)
```python
    if json_dict["relative_lock_height"] > 1000:
        raise ValueError("Relative lock height too high for this pool, cannot join")
```
