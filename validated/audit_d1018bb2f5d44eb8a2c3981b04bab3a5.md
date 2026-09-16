### Title
Unbounded `PostRequest.body` Size Lets an Attacker Freeze ISMP Event Ingestion via Oversized `eth_getLogs` Responses - (File: tesseract/messaging/evm/src/provider.rs)

### Summary
`EvmHost.sol::dispatch(DispatchPost)` places no size limit on the arbitrary `body` bytes it accepts, and the relayer's event-fetching path (`EvmClient::events` / `query_ismp_events`) queries `eth_getLogs` over a full block range in a single call whenever `query_batch_size` is unset. A message dispatcher can pay the (optionally zero) relayer fee and submit `PostRequestEvent` logs with maximal `body` payloads, inflating the byte size of the log response for any block range containing them past common RPC provider limits (the same `-32005`/response-size caps documented elsewhere in this codebase). Because failures from that call are only logged and not retried at a smaller granularity, the events in the failing range are silently dropped rather than eventually delivered.

### Finding Description
`DispatchPost.body` is unrestricted arbitrary bytes accepted directly into the emitted `PostRequestEvent`: [1](#0-0) 

No length check exists on `post.body` before it is committed and emitted, unlike the `Gravity.sol` `deployERC20` function in the original report which similarly accepted unrestricted `_name`/`_symbol`/`_denom` strings.

On the relayer side, `EvmClient::events` fetches all Host logs in the requested range with one `eth_getLogs` call and no byte-size handling: [2](#0-1) 

The caller, `query_ismp_events`, only chunks by a configurable block count (defaulting to `1_000_000_000`, i.e. effectively unbounded/one chunk covering the whole range) and on error just logs and moves on — it does not retry with a smaller window or bisect the query: [3](#0-2) 

The equivalent Substrate-side chunking (`ismp_queryEvents`) shows the same block-count-based (not byte-size-based) chunking pattern with the identical log-and-continue behavior on error: [4](#0-3) 

If a range of blocks contains one or more `PostRequestEvent`s whose combined `body` size pushes the `eth_getLogs` response past the RPC provider's byte/result cap (this repo's own SDK code independently documents this exact RPC failure mode — `-32005`/oversized `eth_getLogs` responses — as a real, frequently-hit condition), `self.client.get_logs(&filter)` returns an error. Since chunking is purely block-count based, reducing the block window does not help if a single block (or even a single transaction/log) already exceeds the size cap; the attacker only needs one block containing a sufficiently large `body`.

### Impact Explanation
Because `query_ismp_events` swallows the error and does not retry with a bisected/smaller query, the `PostRequestEvent`s (and any co-located `PostRequestHandled`, `GetRequestEvent`, `StateMachineUpdated` events) in that block range are never recovered by this call path. This is a route unable to deliver messages: any dispatched request whose log falls in the oversized range is dropped from the relayer's event stream, meaning it is never relayed, timed-out, or otherwise attested, and it silently disappears from the ISMP pipeline for the state machine being watched. Because dispatch fees can legitimately be zero (self-relay), an attacker/dispatcher can trigger this at negligible or no cost, similarly to the original report's ERC20-deploy vector.

### Likelihood Explanation
Likelihood is high on chains where the operator's RPC endpoint enforces the common ~10MB/size or 10k-result `eth_getLogs` cap (documented as a real occurrence in this very repository's own quorum/scanner code for a related component). Any unprivileged account calling `IDispatcher(host).dispatch(post)` on `EvmHost.sol` can set `post.body` to a large arbitrary payload — there is no length validation in `dispatch()` — and doing so repeatedly within one block-scan window is trivial and cheap (bounded only by calldata gas cost, no protocol fee floor tied to size).

### Recommendation
- Enforce a maximum `body` length in `EvmHost.sol::dispatch(DispatchPost)` (and the equivalent Substrate `dispatch_request` path) proportional to a sane multiple of RPC provider caps, or scale the relayer fee/protocol fee with body size to make griefing costly.
- In `EvmClient::events`/`query_ismp_events`, detect an oversized-response/`-32005`-style error from `get_logs` explicitly and bisect the failing block range (recursively halving) rather than only logging and skipping it, so that events are eventually retrieved rather than permanently lost.
- Track and retry failed ranges instead of advancing past them unconditionally.

### Proof of Concept
1. Deploy a HyperApp contract that calls `IDispatcher(host).dispatch(post)` with `post.fee = 0` (self-relay) and `post.body` populated to the maximum size tolerated by the destination chain's calldata/gas limits (e.g., several hundred KB of mostly-zero bytes to minimize gas cost).
2. Submit enough such dispatches within a single relayer polling window (block range) so the aggregate `eth_getLogs` response for `EvmHost`'s address in that range exceeds the configured RPC provider's response-size or result-count cap.
3. Observe `EvmClient::events` (`tesseract/messaging/evm/src/lib.rs:497`) return an error from `self.client.get_logs(&filter)`.
4. Observe `query_ismp_events` (`tesseract/messaging/evm/src/provider.rs:322-333`) log the error and continue to the next chunk without ever recovering the events in the failed range — the dispatched `PostRequestEvent`s are never relayed.

Note: I could not verify the exact byte-size threshold used by any specific production RPC provider integrated with this repo's mainnet deployments, nor confirm whether any external monitoring/alerting would flag such a silent drop before it causes a stuck/timed-out request for the end user.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-959)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
        emit PostRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: _msgSender(),
            to: abi.encodePacked(request.to),
            nonce: request.nonce,
            timeoutTimestamp: request.timeoutTimestamp,
            body: request.body,
            fee: post.fee
        });
    }
```

**File:** tesseract/messaging/evm/src/lib.rs (L485-497)
```rust
	pub async fn events(&self, from: u64, to: u64) -> Result<Vec<Event>, anyhow::Error> {
		use alloy::rpc::types::Filter;
		use alloy_sol_types::SolEvent;
		use ismp::abi::EvmHostEvents;
		use ismp_abi::evm_host::EvmHost::{
			GetRequestEvent, GetRequestHandled, PostRequestEvent, PostRequestHandled,
			StateMachineUpdated as EvmStateMachineUpdated,
		};

		let host_addr = Address::from_slice(&self.ismp_host.0);
		let filter = Filter::new().address(host_addr).from_block(from).to_block(to);

		let logs = self.client.get_logs(&filter).await?;
```

**File:** tesseract/messaging/evm/src/provider.rs (L306-337)
```rust
	async fn query_ismp_events(
		&self,
		previous_height: u64,
		event: StateMachineUpdated,
	) -> Result<Vec<Event>, Error> {
		let full_range = (previous_height + 1)..=event.latest_height;
		if full_range.is_empty() {
			return Ok(Default::default());
		}

		let mut events = vec![];
		let chunk_size = self.config.query_batch_size.unwrap_or(1_000_000_000);
		let chunks = full_range.end().saturating_sub(*full_range.start()) / chunk_size;
		for i in 0..=chunks {
			let start = (i * chunk_size) + *full_range.start();
			let end = if i == chunks { *full_range.end() } else { start + chunk_size - 1 };
			let result = self.events(start, end).await;
			match result {
				Ok(batch) => events.extend(batch),
				Err(err) => {
					log::error!(
						target: crate::LOG_TARGET, "Error while querying events in range {}..{} from {:?}: {err:?}",
						start,
						end,
						self.state_machine
					);
				},
			}
		}

		Ok(events)
	}
```

**File:** tesseract/messaging/substrate/src/provider.rs (L340-381)
```rust
	async fn query_ismp_events(
		&self,
		previous_height: u64,
		event: StateMachineUpdated,
	) -> Result<Vec<Event>, anyhow::Error> {
		let range = (previous_height + 1)..=event.latest_height;
		if range.is_empty() {
			return Ok(Default::default());
		}

		let mut events = vec![];
		let chunk_size = 100;
		let chunks = range.end().saturating_sub(*range.start()) / chunk_size;
		for i in 0..=chunks {
			let start = (i * chunk_size) + *range.start();
			let end = if i == chunks { *range.end() } else { start + chunk_size - 1 };
			let params = rpc_params![
				BlockNumberOrHash::<H256>::Number(start as u32),
				BlockNumberOrHash::<H256>::Number(end as u32)
			];
			let response = self
				.rpc_client
				.request::<HashMap<String, Vec<Event>>>("ismp_queryEvents", params)
				.await;
			match response {
				Ok(response) => {
					let batch = response.values().into_iter().cloned().flatten();
					events.extend(batch)
				},
				Err(err) => {
					log::error!(
						target: crate::LOG_TARGET, "Error while querying events in range {}..{} from {:?}: {err:?}",
						start,
						end,
						self.state_machine
					);
				},
			}
		}

		Ok(events)
	}
```
