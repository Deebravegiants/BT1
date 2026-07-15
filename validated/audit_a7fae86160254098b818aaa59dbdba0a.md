The code evidence is conclusive. Here is the full analysis:

---

### Title
Malformed DID Metadata Causes Permanent Wallet Import Failure via Unhandled TypeError in `did_program_to_metadata` — (`chia/wallet/did_wallet/did_wallet_puzzles.py`)

### Summary

`did_program_to_metadata` performs an unchecked iteration over `program.as_python()` assuming a list-of-pairs structure. An attacker who on-chain encodes DID metadata as a bare atom (e.g., `Program.to(42)`) causes a `TypeError` that propagates up through `create_new_did_wallet_from_coin_spend` → `handle_did` → `determine_coin_type` → `_add_coin_states`. The top-level exception handler catches it but, because `TypeError` is not a `PeerRequestException` or `aiosqlite.Error`, it removes the coin state from the retry store rather than re-queuing it. The victim wallet permanently fails to import the transferred DID.

---

### Finding Description

**Root cause — `did_program_to_metadata`:**

```python
def did_program_to_metadata(program: Program) -> dict[str, str]:
    metadata = {}
    for key, val in program.as_python():   # ← no guard on structure
        metadata[str(key, "utf-8")] = str(val, "utf-8")
    return metadata
```

If `program` is a bare atom (e.g., `Program.to(42)`), `program.as_python()` returns `b'\x2a'`. Iterating over bytes yields integers; unpacking an integer as `key, val` raises `TypeError: cannot unpack non-iterable int object`. [1](#0-0) 

**Call site — `create_new_did_wallet_from_coin_spend`:**

The call at line 234 has no try/except:
```python
metadata=json.dumps(did_wallet_puzzles.did_program_to_metadata(metadata)),
``` [2](#0-1) 

The `metadata` variable comes directly from uncurrying the on-chain inner puzzle:
```python
_, recovery_list_hash, num_verification, _, metadata = args
``` [3](#0-2) 

**Trigger path — `handle_did`:**

`handle_did` calls `create_new_did_wallet_from_coin_spend` at line 1472 with no exception handling: [4](#0-3) 

**Fatal exception handling — `_add_coin_states`:**

The top-level handler at line 2227–2234 catches the `TypeError`, but because it is not a `PeerRequestException` or `aiosqlite.Error`, it takes the `else` branch and **removes** the coin state from the retry store instead of re-queuing it:

```python
except Exception as e:
    self.log.exception(f"Failed to add coin_state: {coin_state}, error: {e}")
    if rollback_wallets is not None:
        self.wallets = rollback_wallets
    if isinstance(e, (PeerRequestException, aiosqlite.Error)):
        await self.retry_store.add_state(coin_state, peer.peer_node_id, fork_height)
    else:
        await self.retry_store.remove_state(coin_state)   # ← permanent drop
    continue
``` [5](#0-4) 

The same unguarded call to `did_program_to_metadata` also exists in `find_lost_did` at line 3456, making the `find_lost_did` RPC path equally vulnerable. [6](#0-5) 

---

### Impact Explanation

The victim wallet permanently cannot import the transferred DID. Every sync attempt (including full resyncs) re-executes the same deterministic code path and fails identically. The DID singleton remains on-chain but the victim has no wallet record for it and cannot spend it. This satisfies the **High** impact criterion: *permanent inability for honest wallets to process valid sync updates under normal network assumptions*.

---

### Likelihood Explanation

The attacker needs only to:
1. Create a DID with `Program.to(42)` (or any non-list CLVM atom) as the metadata argument in the curried inner puzzle — CLVM consensus does not validate metadata structure.
2. Transfer the DID to the victim's puzzle hash via a standard DID transfer spend.

No leaked keys, admin access, or broken cryptography is required. The spend bundle is valid on-chain; only the wallet-side Python parsing fails.

---

### Recommendation

Wrap the iteration in `did_program_to_metadata` with a try/except and return an empty dict (or a best-effort partial result) on malformed input:

```python
def did_program_to_metadata(program: Program) -> dict[str, str]:
    metadata = {}
    try:
        for key, val in program.as_python():
            try:
                metadata[str(key, "utf-8")] = str(val, "utf-8")
            except (TypeError, ValueError, UnicodeDecodeError):
                continue
    except (TypeError, ValueError):
        pass
    return metadata
```

Additionally, the `else: retry_store.remove_state` branch in `_add_coin_states` should be reviewed — a `TypeError` from wallet-side parsing should arguably not permanently discard the coin state.

---

### Proof of Concept

```python
from chia.types.blockchain_format.program import Program
from chia.wallet.did_wallet.did_wallet_puzzles import did_program_to_metadata

# Bare integer atom
try:
    did_program_to_metadata(Program.to(42))
    assert False, "Should have raised"
except TypeError as e:
    print(f"Confirmed crash: {e}")

# Bare bytes atom
try:
    did_program_to_metadata(Program.to(b"raw"))
    assert False, "Should have raised"
except TypeError as e:
    print(f"Confirmed crash: {e}")
```

Both calls raise `TypeError: cannot unpack non-iterable int object`, confirming the vulnerability without any network setup.

### Citations

**File:** chia/wallet/did_wallet/did_wallet_puzzles.py (L217-225)
```python
def did_program_to_metadata(program: Program) -> dict[str, str]:
    """
    Convert a program to a metadata dict
    :param program: Chialisp program contains the metadata
    :return: Metadata dict
    """
    metadata = {}
    for key, val in program.as_python():
        metadata[str(key, "utf-8")] = str(val, "utf-8")
```

**File:** chia/wallet/did_wallet/did_wallet.py (L209-209)
```python
        _, recovery_list_hash, num_verification, _, metadata = args
```

**File:** chia/wallet/did_wallet/did_wallet.py (L234-234)
```python
            metadata=json.dumps(did_wallet_puzzles.did_program_to_metadata(metadata)),
```

**File:** chia/wallet/wallet_state_manager.py (L1472-1479)
```python
                did_wallet = await DIDWallet.create_new_did_wallet_from_coin_spend(
                    self,
                    self.main_wallet,
                    launch_coin.coin,
                    did_puzzle,
                    coin_spend,
                    f"DID {encode_puzzle_hash(launch_id, AddressType.DID.hrp(self.config))}",
                )
```

**File:** chia/wallet/wallet_state_manager.py (L2227-2235)
```python
            except Exception as e:
                self.log.exception(f"Failed to add coin_state: {coin_state}, error: {e}")
                if rollback_wallets is not None:
                    self.wallets = rollback_wallets  # Restore since DB will be rolled back by writer
                if isinstance(e, (PeerRequestException, aiosqlite.Error)):
                    await self.retry_store.add_state(coin_state, peer.peer_node_id, fork_height)
                else:
                    await self.retry_store.remove_state(coin_state)
                continue
```

**File:** chia/wallet/wallet_state_manager.py (L3456-3456)
```python
                        json.dumps(did_program_to_metadata(metadata)),
```
