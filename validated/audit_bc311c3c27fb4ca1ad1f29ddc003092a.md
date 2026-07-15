### Title
`PoolWallet.target_state` Is Never Persisted — Pool Exit Permanently Stalls After Wallet Restart - (File: chia/pools/pool_wallet.py)

### Summary

`PoolWallet` stores three critical fields — `target_state`, `next_transaction_fee`, and `next_tx_config` — only in memory. They are never written to the database. When the wallet is reloaded from the database (e.g., after any restart), `create_from_db()` initialises all three to their zero-value defaults. The automatic second-step travel transaction that completes a pool exit is driven entirely by `new_peak()`, which returns immediately when `target_state is None`. A user who restarts their wallet while the singleton is in `LEAVING_POOL` state will find the exit permanently stalled, with pool rewards continuing to flow to the pool's address for an indefinite period.

### Finding Description

`PoolWallet` is a Python dataclass with three instance fields that carry the in-flight pool-transition state:

```python
# chia/pools/pool_wallet.py  lines 78-80
next_transaction_fee: uint64 = uint64(0)
next_tx_config: TXConfig = DEFAULT_TX_CONFIG
target_state: PoolState | None = None
``` [1](#0-0) 

These fields are set when the user calls `join_pool()` or `self_pool()`:

```python
# join_pool(), lines 668-670
self.target_state = target_state
self.next_transaction_fee = fee
self.next_tx_config = action_scope.config.tx_config
``` [2](#0-1) 

```python
# self_pool(), lines 704-708
self.target_state = create_pool_state(...)
self.next_transaction_fee = fee
self.next_tx_config = action_scope.config.tx_config
``` [3](#0-2) 

When the wallet is reconstructed from the database, `create_from_db()` creates a fresh `PoolWallet` object with no attempt to restore these fields:

```python
@classmethod
async def create_from_db(cls, wallet_state_manager, wallet, wallet_info, name=None) -> PoolWallet:
    """This creates a PoolWallet from DB. However, all data is already handled by
    WalletPoolStore, so we don't need to do anything here."""
    pool_wallet = cls(
        wallet_state_manager=wallet_state_manager,
        log=logging.getLogger(name if name else __name__),
        wallet_info=wallet_info,
        wallet_id=wallet_info.id,
        standard_wallet=wallet,
    )
    return pool_wallet
``` [4](#0-3) 

After reload, `target_state` is always `None`. The automatic second-step submission in `new_peak()` is gated on this field:

```python
async def new_peak(self, peak_height: uint32) -> None:
    ...
    if self.target_state is None:
        return          # ← always taken after restart
``` [5](#0-4) 

The second travel transaction — which moves the singleton from `LEAVING_POOL` to the final state — is only submitted from `new_peak()`:

```python
async with self.wallet_state_manager.new_action_scope(self.next_tx_config, push=True) as action_scope:
    await self.generate_travel_transactions(self.next_transaction_fee, action_scope)
``` [6](#0-5) 

Because `target_state`, `next_transaction_fee`, and `next_tx_config` are never written to any persistent store, they are lost on every wallet restart. This is the direct Python analog of the Solidity `memory` vs. `storage` bug: state is updated in a transient object but never written back to the origin.

### Impact Explanation

A pool exit requires two on-chain transactions:

1. **First transaction** (submitted immediately): moves the singleton from `FARMING_TO_POOL` → `LEAVING_POOL`.
2. **Second transaction** (submitted automatically by `new_peak()` after `relative_lock_height` blocks): moves the singleton from `LEAVING_POOL` → `SELF_POOLING` or a new pool.

The window between these two transactions spans `relative_lock_height` blocks (minimum 5, maximum 1,000 per `MINIMUM_RELATIVE_LOCK_HEIGHT` / `MAXIMUM_RELATIVE_LOCK_HEIGHT`). Any wallet restart during this window resets `target_state = None`. After restart, `new_peak()` returns immediately and the second transaction is never submitted automatically. The singleton remains permanently in `LEAVING_POOL`, and all pool block rewards continue to be directed to the pool's `p2_singleton` address rather than the farmer's own wallet. This constitutes **pool payout redirection** and **corruption of pool membership state** with direct financial impact.

### Likelihood Explanation

Wallet restarts are routine (daemon restart, OS reboot, upgrade). The `LEAVING_POOL` window is at minimum 5 blocks (~1 minute on mainnet) but commonly 32–100 blocks. Any restart during this window silently stalls the exit. The user receives no error; `pw_status` still shows `LEAVING_POOL` with `target = None`, which looks like a completed first step rather than a broken state.

### Recommendation

Persist `target_state`, `next_transaction_fee`, and `next_tx_config` to the database. The simplest approach is to store them in the existing `WalletInfo.data` JSON blob (already used by other wallet types) and restore them in `create_from_db()`. Alternatively, add a dedicated column to the pool state transitions table. At minimum, `target_state` must be persisted so that `new_peak()` can resume the exit after any restart.

### Proof of Concept

1. Create a pool wallet farming to a pool (`FARMING_TO_POOL`).
2. Call `pw_self_pool` (or `pw_join_pool`) — this sets `self.target_state` in memory and submits the first travel transaction, moving the singleton to `LEAVING_POOL`.
3. Before `relative_lock_height` blocks pass, restart the wallet daemon.
4. After restart, `create_from_db()` reconstructs `PoolWallet` with `target_state = None`.
5. Observe that `new_peak()` returns immediately on every new block (`if self.target_state is None: return`).
6. The singleton remains in `LEAVING_POOL` indefinitely; pool rewards continue flowing to the pool's address. The user must manually re-call `pw_self_pool` to re-set `target_state` in memory — but this is not documented and the wallet gives no indication that action is required.

### Citations

**File:** chia/pools/pool_wallet.py (L78-80)
```python
    next_transaction_fee: uint64 = uint64(0)
    next_tx_config: TXConfig = DEFAULT_TX_CONFIG
    target_state: PoolState | None = None
```

**File:** chia/pools/pool_wallet.py (L369-388)
```python
    @classmethod
    async def create_from_db(
        cls,
        wallet_state_manager: Any,
        wallet: Wallet,
        wallet_info: WalletInfo,
        name: str | None = None,
    ) -> PoolWallet:
        """
        This creates a PoolWallet from DB. However, all data is already handled by WalletPoolStore, so we don't need
        to do anything here.
        """
        pool_wallet = cls(
            wallet_state_manager=wallet_state_manager,
            log=logging.getLogger(name if name else __name__),
            wallet_info=wallet_info,
            wallet_id=wallet_info.id,
            standard_wallet=wallet,
        )
        return pool_wallet
```

**File:** chia/pools/pool_wallet.py (L668-670)
```python
        self.target_state = target_state
        self.next_transaction_fee = fee
        self.next_tx_config = action_scope.config.tx_config
```

**File:** chia/pools/pool_wallet.py (L704-708)
```python
        self.target_state = create_pool_state(
            SELF_POOLING, owner_puzzlehash, owner_pubkey, pool_url=None, relative_lock_height=uint32(0)
        )
        self.next_transaction_fee = fee
        self.next_tx_config = action_scope.config.tx_config
```

**File:** chia/pools/pool_wallet.py (L813-814)
```python
        if self.target_state is None:
            return
```

**File:** chia/pools/pool_wallet.py (L849-850)
```python
                async with self.wallet_state_manager.new_action_scope(self.next_tx_config, push=True) as action_scope:
                    await self.generate_travel_transactions(self.next_transaction_fee, action_scope)
```
