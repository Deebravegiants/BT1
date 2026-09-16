## Analog Found

### Title
Missing Input Validation on `EvmHost.dispatch()` (DispatchPost/DispatchGet) Permits Permanent Freezing of Relayer Fees - (File: evm/src/core/EvmHost.sol)

### Summary
The Futaba `Gateway.query()` bug class — accepting `dstChainId`, `height`, `slot`, and `message` without validating they are non-zero/non-empty — has a direct analog in Hyperbridge's `EvmHost.dispatch()` entry points. Both the `DispatchPost` and `DispatchGet` overloads of `dispatch()` accept attacker-controlled `dest`, `to`, `body`, `keys`, and `height` fields with no validation whatsoever before committing a relayer fee and emitting the event that relayers act on.

### Finding Description
`EvmHost.dispatch(DispatchPost memory post)` collects `post.fee` (via native-to-feeToken swap or `safeTransferFrom`), then builds and commits a `PostRequest` using `post.dest`, `post.to`, and `post.body` verbatim, with zero checks on their contents: [1](#0-0) 

Likewise `dispatch(DispatchGet memory get)` commits a `GetRequest` from `get.dest`, `get.height`, and `get.keys` with no validation that `dest` is a recognized/routable state machine id, that `keys` is non-empty, or that `height` is sensible: [2](#0-1) 

In both functions the `timeout` is resolved as `post.timeout == 0 ? 0 : block.timestamp + timeout`, and `0` is explicitly documented protocol-wide as "no timeout ... messages will never expire": [3](#0-2) 

The same pattern exists on the Substrate side: `pallet_ismp`'s `IsmpDispatcher::dispatch_request` collects the fee and commits the request built from caller-supplied `dest`/`to`/`body`/`keys` with no validation, and also allows `timeout == 0` to mean "never times out": [4](#0-3) [5](#0-4) 

Because `dest` (state machine identifier) is free-form `bytes`/`StateMachine` with no membership check against a known/configured consensus client or routable destination, and `to`/`body`/`keys` can be empty, a caller can dispatch a request that:
1. Targets a destination for which Hyperbridge has (or will ever have) no consensus client / state commitment, so no relayer can ever produce a valid delivery or timeout proof for it, and
2. Sets `timeout = 0`, which per the documented semantics means the request can never be rejected as timed out (`req.timed_out()` on the destination/response handlers is keyed off a non-zero, exceeded timeout, cf. `modules/ismp/core/src/handlers/response.rs` timeout check pattern) so the fee-refund-on-timeout path is unreachable.

### Impact Explanation
The relayer fee for the dispatched request (`post.fee`/`get.fee`, escrowed in `_requestCommitments`/`RequestCommitments`) can never be recovered: it cannot be delivered (invalid/non-existent destination), and it cannot time out (timeout = 0, "never expires"). This is a permanent freezing-of-funds condition for any user/app dispatching through a misconfigured or malicious (invalid `dest`) call — matching the impact class accepted by the rules ("permanent freezing of funds"). Any unprivileged app contract or user calling `IDispatcher.dispatch()` can trigger this, satisfying the requirement for reachability from an unprivileged dispatcher.

### Likelihood Explanation
Medium: this requires a dispatching application (or a misconfigured integrator) to pass an invalid `dest`/empty `to`/`body`/`keys` and `timeout = 0`. Since none of these fields are validated at the protocol layer (`EvmHost.dispatch`, `pallet_ismp::dispatch_request`), any downstream application bug, encoding mistake, or malicious low-value griefing dispatch reproduces this condition without any special privilege, matching the original Futaba finding's likelihood profile of "unvalidated struct fields accepted directly from calldata."

### Recommendation
Add the same class of checks recommended in the original Futaba report to `EvmHost.dispatch(DispatchPost)` / `dispatch(DispatchGet)` (and the analogous `pallet_ismp` dispatcher):
- Revert if `dest`/`to`/`body` (for POST) or `dest`/`keys` (for GET) are empty.
- Optionally validate `dest` resolves to a state machine with a known/registered consensus client before escrowing any fee.
- Consider disallowing `timeout == 0` for fee-bearing requests, or bounding how long a zero-timeout, fee-locked request can remain unclaimed before an emergency refund path is available.

### Proof of Concept
1. Deploy/point at `EvmHost` and call:
   ```solidity
   host.dispatch(DispatchPost({
       body: "",                       // empty body, never validated
       dest: "EVM-999999999",          // unroutable/unknown destination, never validated
       timeout: 0,                     // "never times out" per docs
       to: "",                         // empty recipient module
       fee: 100e18,                    // fee collected via safeTransferFrom
       payer: msg.sender
   }));
   ``` [1](#0-0) 
2. `_requestCommitments[commitment]` now holds `fee = 100e18` for `payer`.
3. No consensus client exists for `EVM-999999999`, so no relayer can ever submit a valid delivery or timeout proof for this commitment; `timeout == 0` also means the timeout-message path (`req.timed_out()`) never triggers.
4. `fundRequest` only increases the stuck fee further; there is no path to reclaim `fee` for this commitment — the funds are permanently frozen.

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

**File:** evm/src/core/EvmHost.sol (L974-1013)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }

        uint64 timeoutTimestamp = get.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(get.timeout);
        GetRequest memory request = GetRequest({
            source: host(),
            dest: get.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            timeoutTimestamp: timeoutTimestamp,
            keys: get.keys,
            height: get.height,
            context: get.context
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
        emit GetRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: request.from,
            keys: request.keys,
            nonce: request.nonce,
            height: request.height,
            context: request.context,
            timeoutTimestamp: request.timeoutTimestamp,
            fee: get.fee
        });
    }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L27-34)
```text
    // timeout for this request in seconds
    uint64 timeout;
    // The amount put up to be paid to the relayer, 
    // this is in the feeToken and charged to msg.sender
    uint256 fee;
    // who pays for this request?
    address payer;
}
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L92-151)
```rust
	fn dispatch_request(
		&self,
		request: DispatchRequest,
		fee: FeeMetadata<T>,
	) -> Result<H256, anyhow::Error> {
		// collect payment for the request
		if fee.fee != Zero::zero() {
			T::Currency::transfer(
				&fee.payer,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| IsmpError::Custom(format!("Error withdrawing request fees: {err:?}")))?;
		}

		let request = match request {
			DispatchRequest::Get(dispatch_get) => {
				let get = GetRequest {
					source: self.host_state_machine(),
					dest: dispatch_get.dest,
					nonce: self.next_nonce(),
					from: dispatch_get.from,
					keys: dispatch_get.keys,
					height: dispatch_get.height,
					context: dispatch_get.context,
					timeout_timestamp: if dispatch_get.timeout == 0 {
						0
					} else {
						<T::TimestampProvider as UnixTime>::now()
							.as_secs()
							.saturating_add(dispatch_get.timeout)
					},
				};
				Request::Get(get)
			},
			DispatchRequest::Post(dispatch_post) => {
				let post = PostRequest {
					source: self.host_state_machine(),
					dest: dispatch_post.dest,
					nonce: self.next_nonce(),
					from: dispatch_post.from,
					to: dispatch_post.to,
					timeout_timestamp: if dispatch_post.timeout == 0 {
						0
					} else {
						<T::TimestampProvider as UnixTime>::now()
							.as_secs()
							.saturating_add(dispatch_post.timeout)
					},
					body: dispatch_post.body,
				};
				Request::Post(post)
			},
		};

		let commitment = Pallet::<T>::dispatch_request(request, fee)?;

		Ok(commitment)
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L90-121)
```rust
	pub fn dispatch_request(request: Request, meta: FeeMetadata<T>) -> Result<H256, ismp::Error> {
		let commitment = hash_request::<Pallet<T>>(&request);

		if RequestCommitments::<T>::contains_key(commitment) {
			Err(ismp::Error::Custom("Duplicate request".to_string()))?
		}

		let (dest_chain, source_chain, nonce) =
			(request.dest_chain(), request.source_chain(), request.nonce());
		let leaf_index_and_pos = T::OffchainDB::push(Leaf::Request(request));
		// Deposit Event
		Pallet::<T>::deposit_event(Event::Request {
			request_nonce: nonce,
			source_chain,
			dest_chain,
			commitment,
		});

		RequestCommitments::<T>::insert(
			commitment,
			RequestMetadata {
				offchain: LeafIndexAndPos {
					leaf_index: leaf_index_and_pos.index,
					pos: leaf_index_and_pos.position,
				},
				fee: meta,
				claimed: false,
			},
		);

		Ok(commitment)
	}
```
