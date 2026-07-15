### Title
Zero-Division in `get_current_authentication_token` When Malicious Pool Sets `authentication_token_timeout=0` Permanently Blocks Farmer Partial Submission — (File: `chia/protocols/pool_protocol.py`)

---

### Summary

`get_current_authentication_token` in `chia/protocols/pool_protocol.py` divides by the `timeout` parameter with no guard for zero. A malicious pool operator can return `authentication_token_timeout: 0` in their `/pool_info` HTTP response. The farmer stores this value without validation, and every subsequent partial-submission attempt raises `ZeroDivisionError`, permanently preventing the farmer from earning pool rewards until they manually leave the pool.

---

### Finding Description

**Root cause — no zero-check on the divisor:** [1](#0-0) 

```python
def get_current_authentication_token(timeout: uint8) -> uint64:
    return uint64(int(time.time() / 60) / timeout)   # ZeroDivisionError if timeout == 0
```

**The value originates from an untrusted pool HTTP response:**

`authentication_token_timeout` is declared as a plain `uint8` in `GetPoolInfoResponse` with no minimum-value constraint: [2](#0-1) 

**The farmer stores it without validation:** [3](#0-2) 

```python
pool_state["authentication_token_timeout"] = pool_info.authentication_token_timeout
```

**Crash site 1 — partial submission in `new_proof_of_space`:** [4](#0-3) 

```python
payload = PostPartialPayload(
    pool_state_dict["pool_config"].launcher_id,
    get_current_authentication_token(authentication_token_timeout),  # raises ZeroDivisionError
    ...
)
```

There is no `try/except` around this call inside `new_proof_of_space`; the exception propagates to the API framework, silently dropping every partial for plots associated with the malicious pool.

**Crash site 2 — `_pool_get_farmer` (GET /farmer):** [5](#0-4) 

```python
authentication_token = get_current_authentication_token(authentication_token_timeout)
```

Called from `update_pool_state`; the outer `try/except` catches the error and logs it, but the farmer state is never updated, so the broken timeout persists indefinitely.

**`validate_authentication_token` is equally broken:** [6](#0-5) 

```python
def validate_authentication_token(token: uint64, timeout: uint8) -> bool:
    return abs(token - get_current_authentication_token(timeout)) <= timeout
```

---

### Impact Explanation

Once a farmer joins a pool that advertises `authentication_token_timeout=0`:

1. Every proof of space found for plots bound to that pool triggers `ZeroDivisionError` in `new_proof_of_space`, silently discarding the partial.
2. Every periodic `GET /farmer` call in `update_pool_state` also raises `ZeroDivisionError`, preventing difficulty synchronisation.
3. The farmer earns **zero pool rewards** for all affected plots for as long as they remain in the pool.
4. The farmer has no automatic recovery path; manual intervention (leaving the pool) is required.

This is a **permanent, long-lived inability for an honest farmer to process pool actions**, matching the High impact category.

---

### Likelihood Explanation

Any entity that can operate an HTTP server can become a Chia pool operator — no privileged Chia keys or consensus access is required. The attacker simply returns `"authentication_token_timeout": 0` in the `/pool_info` JSON response. The farmer code accepts any `uint8` value (0–255) without validation. The attack is trivially reproducible and requires no cryptographic capability.

---

### Recommendation

Add a lower-bound guard at the point of receipt, before the value is stored:

```python
# In farmer.py, after receiving pool_info:
if pool_info.authentication_token_timeout == 0:
    self.log.error(
        f"Pool {pool_config.pool_url} returned invalid "
        "authentication_token_timeout=0; skipping update."
    )
    pool_state["next_pool_info_update"] = time.time() + UPDATE_POOL_INFO_FAILURE_RETRY_INTERVAL
    continue
```

Alternatively, add a defensive guard inside the function itself:

```python
def get_current_authentication_token(timeout: uint8) -> uint64:
    if timeout == 0:
        raise ValueError("authentication_token_timeout must be > 0")
    return uint64(int(time.time() / 60) / timeout)
```

---

### Proof of Concept

1. Stand up an HTTP server that responds to `GET /pool_info` with a valid `GetPoolInfoResponse` JSON body except `"authentication_token_timeout": 0`.
2. Have a farmer with plotNFT plots join this pool via `chia plotnft join`.
3. The farmer calls `update_pool_state()`, receives the response, and stores `authentication_token_timeout = uint8(0)` with no error.
4. When the harvester finds a proof of space for any plot whose `pool_contract_puzzle_hash` matches the malicious pool, `farmer_api.py` calls `get_current_authentication_token(uint8(0))`, raising `ZeroDivisionError`.
5. The partial is silently dropped; the farmer receives no pool reward for that proof. This repeats for every subsequent proof of space, indefinitely.

### Citations

**File:** chia/protocols/pool_protocol.py (L48-57)
```python
class GetPoolInfoResponse(Streamable):
    name: str
    logo_url: str
    minimum_difficulty: uint64
    relative_lock_height: uint32
    protocol_version: uint8
    fee: str
    description: str
    target_puzzle_hash: bytes32
    authentication_token_timeout: uint8
```

**File:** chia/protocols/pool_protocol.py (L169-170)
```python
def get_current_authentication_token(timeout: uint8) -> uint64:
    return uint64(int(time.time() / 60) / timeout)
```

**File:** chia/protocols/pool_protocol.py (L174-175)
```python
def validate_authentication_token(token: uint64, timeout: uint8) -> bool:
    return abs(token - get_current_authentication_token(timeout)) <= timeout
```

**File:** chia/farmer/farmer.py (L398-398)
```python
        authentication_token = get_current_authentication_token(authentication_token_timeout)
```

**File:** chia/farmer/farmer.py (L611-612)
```python
                        pool_info = pool_info_result.pool_info
                        pool_state["authentication_token_timeout"] = pool_info.authentication_token_timeout
```

**File:** chia/farmer/farmer_api.py (L271-278)
```python
                payload = PostPartialPayload(
                    pool_state_dict["pool_config"].launcher_id,
                    get_current_authentication_token(authentication_token_timeout),
                    new_proof_of_space.proof,
                    new_proof_of_space.sp_hash,
                    is_eos,
                    peer.peer_node_id,
                )
```
