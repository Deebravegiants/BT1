### Title
Pool Server 301/308 Redirect Stores Unvalidated URL, Enabling Payout Redirection via Authentication Token Capture — (File: chia/farmer/farmer.py)

---

### Summary

In `chia/farmer/farmer.py`, the `_pool_get_pool_info` method follows HTTP 301/308 redirects from a pool server and stores the redirect destination as the new persistent `pool_url` **without validating it against HTTPS requirements or private-network ranges**. On the next update cycle, the farmer sends signed authentication tokens, owner signatures, and payout instructions to the attacker-controlled URL. A malicious pool operator can use the captured tokens to authenticate to the legitimate pool and change the farmer's payout instructions, redirecting pool rewards to the attacker's address.

---

### Finding Description

`_pool_get_pool_info` in `chia/farmer/farmer.py` makes a GET request to `{pool_config.pool_url}/pool_info`. If the response was reached via a chain of HTTP 301 or 308 redirects, the final URL is extracted and returned as `new_pool_url`: [1](#0-0) 

In `update_pool_state`, this value is written directly to the persistent pool config with no URL validation: [2](#0-1) 

The `enforce_https` guard only validates the **currently stored** `pool_config.pool_url` at the top of each update cycle, before the GET request is made: [3](#0-2) 

It does **not** validate the redirect destination before persisting it. On the next `update_pool_state` cycle, the farmer loads the new attacker-controlled URL from `PoolingShareState` and uses it for all subsequent pool communications:

- `_pool_get_farmer` — sends a signed authentication token [4](#0-3) 
- `_pool_post_farmer` — sends signed authentication token + payout instructions + owner signature [5](#0-4) 
- `_pool_put_farmer` — same payload [6](#0-5) 
- `new_proof_of_space` in `farmer_api.py` — sends signed proof-of-space partials [7](#0-6) 

The `payout_instructions` field in `PoolingShareState` is the XCH puzzle hash to which the pool pays out rewards: [8](#0-7) 

---

### Impact Explanation

A malicious pool operator issues a 301 redirect from their `/pool_info` endpoint to an attacker-controlled server. The farmer's `pool_url` is silently updated to the attacker's server. On the next update cycle, the farmer sends a POST /farmer request containing:
- A signed `PostFarmerPayload` (authentication public key, authentication token, payout instructions)
- An owner-key signature over that payload

The attacker captures the authentication token and uses it to call PUT /farmer on the **legitimate** pool with modified `payout_instructions` pointing to the attacker's XCH address. Pool rewards are then redirected to the attacker. This matches the allowed High impact: **payout redirection** and **bypass of pool authorization enabling unauthorized payout redirection**.

On non-mainnet networks the redirect can target `http://127.0.0.1/...` or RFC-1918 addresses, constituting a full SSRF against local services.

---

### Likelihood Explanation

The attacker must operate (or compromise) a pool that the farmer has joined. Pool operators are semi-trusted: they are expected to serve pool protocol responses, but not to redirect the farmer's authentication credentials to a third-party server. The attack is persistent because the new URL is written to the YAML config file and survives farmer restarts. The farmer has no indication that its pool URL has changed.

---

### Recommendation

1. **Validate the redirect target URL** before storing it: apply the same `enforce_https` check to `new_pool_url` that is applied to `pool_config.pool_url`.
2. **Reject cross-origin redirects**: only accept 301/308 redirects that stay within the same registered domain as the original pool URL.
3. **Block private-network redirect targets**: reject any `new_pool_url` whose host resolves to RFC-1918, loopback, or link-local ranges.
4. **Notify the operator**: log a prominent warning (or refuse to update) when a redirect would change the pool URL, so the farmer operator can verify the change.

---

### Proof of Concept

1. Attacker operates a pool at `https://malicious-pool.com` and a capture server at `https://attacker-capture.com`.
2. Farmer joins the pool; `pool_url = "https://malicious-pool.com"` is written to `PoolingShareState`.
3. `update_pool_state` fires; `enforce_https` passes (URL starts with `https://`).
4. Farmer GETs `https://malicious-pool.com/pool_info`; pool responds HTTP 301 → `https://attacker-capture.com/pool_info`.
5. `aiohttp` follows the redirect; `resp.url = "https://attacker-capture.com/pool_info"`.
6. `new_pool_url = "https://attacker-capture.com"` is returned and written to config.
7. Next `update_pool_state` cycle: `pool_config.pool_url = "https://attacker-capture.com"` passes `enforce_https`.
8. Farmer POSTs to `https://attacker-capture.com/farmer` with `PostFarmerRequest` containing the authentication token, authentication public key, payout instructions, and an owner-key BLS signature.
9. Attacker extracts the authentication token and calls `PUT https://malicious-pool.com/farmer` with the farmer's `launcher_id`, the captured token, and modified `payout_instructions` set to the attacker's XCH address.
10. The legitimate pool updates the farmer's payout address; all future pool rewards are paid to the attacker.

### Citations

**File:** chia/farmer/farmer.py (L372-381)
```python
                        new_pool_url: str | None = None
                        response_url_str = f"{resp.url}"
                        if (
                            response_url_str != url
                            and len(resp.history) > 0
                            and all(r.status in {301, 308} for r in resp.history)
                        ):
                            new_pool_url = response_url_str.replace("/pool_info", "")

                        return GetPoolInfoResult(pool_info=pool_info, new_pool_url=new_pool_url)
```

**File:** chia/farmer/farmer.py (L411-415)
```python
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.get(
                    f"{pool_config.pool_url}/farmer",
                    params=get_farmer_params,
                    ssl=ssl_context_for_root(get_mozilla_ca_crt(), log=self.log),
```

**File:** chia/farmer/farmer.py (L459-463)
```python
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{pool_config.pool_url}/farmer",
                    json=post_farmer_request.to_json_dict(),
                    ssl=ssl_context_for_root(get_mozilla_ca_crt(), log=self.log),
```

**File:** chia/farmer/farmer.py (L507-511)
```python
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{pool_config.pool_url}/farmer",
                    json=put_farmer_request.to_json_dict(),
                    ssl=ssl_context_for_root(get_mozilla_ca_crt(), log=self.log),
```

**File:** chia/farmer/farmer.py (L600-603)
```python
                enforce_https = config["full_node"]["selected_network"] == "mainnet"
                if enforce_https and not pool_config.pool_url.startswith("https://"):
                    self.log.error(f"Pool URLs must be HTTPS on mainnet {pool_config.pool_url}")
                    continue
```

**File:** chia/farmer/farmer.py (L619-623)
```python
                    if pool_info_result is not None and pool_info_result.new_pool_url is not None:
                        with PoolingShareState.acquire(
                            root_path=self._root_path, p2_singleton_puzzle_hash=p2_singleton_puzzle_hash
                        ) as editable_pool_config:
                            editable_pool_config.pool_url = pool_info_result.new_pool_url
```

**File:** chia/farmer/farmer_api.py (L365-370)
```python
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{pool_url}/partial",
                            json=post_partial_request.to_json_dict(),
                            ssl=ssl_context_for_root(get_mozilla_ca_crt(), log=self.farmer.log),
                            headers={
```

**File:** chia/pools/pool_config.py (L30-38)
```python
@dataclass(kw_only=True)
class PoolingShareState:
    launcher_id: bytes32
    pool_url: str
    payout_instructions: str
    target_puzzle_hash: bytes32
    p2_singleton_puzzle_hash: bytes32
    owner_public_key: G1Element
    key_derivation_index: int
```
