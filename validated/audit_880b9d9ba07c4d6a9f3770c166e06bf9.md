### Title
Setting `timeout=0` on a HyperFungibleToken cross-chain send permanently disables timeout recovery, freezing burned/locked funds forever if delivery fails - ([File: sdk/packages/core/contracts/libraries/Message.sol])

### Summary
`HyperFungibleToken.send()` and `WrappedHyperFungibleToken.send()` let any unprivileged user burn (or lock) tokens and dispatch an ISMP `PostRequest` cross-chain, specifying an arbitrary `timeout` in `SendParams`. This is directly analogous to the reported `SablierV2MerkleLockup` bug: if a configuration parameter that gates recovery is set incorrectly (there, an unset expiration; here, `timeout == 0`), the only recovery mechanism (there, `clawback()`; here, `handlePostRequestTimeouts` → `onPostRequestTimeout`) becomes permanently unavailable, and funds cannot ever be recovered.

### Finding Description
When a user calls `send()`, `EvmHost.dispatch()` computes the request's absolute timeout: [1](#0-0) 
`timeoutTimestamp` is set to `0` whenever `post.timeout == 0`. The `Message` library then interprets a `timeoutTimestamp` of `0` as "no expiration" and returns `type(uint64).max` from `timeout()`: [2](#0-1) 

The ISMP timeout handler (`modules/ismp/core/src/handlers/timeout.rs`) only allows a `PostRequest` timeout to be processed once `post.timed_out(state.timestamp())` is true, i.e., once the destination's timestamp exceeds `post.timeout()`: [3](#0-2) [4](#0-3) 

Because a `timeoutTimestamp` of `0` is deliberately mapped to `uint64.max` ("no expiration"), a request dispatched with `timeout: 0` can never satisfy `timed_out()`. Consequently `handlePostRequestTimeouts` will always revert with `RequestTimeoutNotElapsed`/`MessageNotTimedOut`, and `onPostRequestTimeout` (which re-mints burned tokens or unlocks locked tokens back to the sender) can never be invoked: [5](#0-4) 

If the message subsequently fails to be delivered on the destination chain for any reason — the destination chain/peer was misconfigured (`UnsupportedChain`), the sender used an unregistered/incorrect peer address (`UnauthorizedSource`), the destination gateway is paused, or the relayer simply never submits it — there is no other path to recover the burned/locked tokens. The `onAccept()` gate on the destination shows how easily delivery can permanently fail due to configuration: [6](#0-5) 

This mirrors the MerkleLockup pattern exactly: a caller-controllable parameter (`expiration` there, `timeout` here) that both gates the sole recovery function and can be set to a value ("unset"/`0`) that disables that recovery function permanently.

### Impact Explanation
Any unprivileged sender who dispatches a `HyperFungibleToken`/`WrappedHyperFungibleToken` transfer with `timeout = 0` (or relies on an SDK/integration default of `0`) permanently loses access to the burned or escrowed tokens if the message is never successfully delivered — whether due to their own misconfiguration of `to`/`dest`, destination-side pausing, an unregistered peer, or simple relayer non-delivery. Since `send()`/`_buildDispatchPost()` place no floor on `params.timeout` (unlike `IntentGatewayV2.fillOrder`'s `validUntil` bound checks), this is trivially reachable by any single transaction from a single user and results in a permanent, unrecoverable freeze of the sender's own funds — a direct token-bridge fund-freezing bug of Medium/High severity.

### Likelihood Explanation
Likelihood is meaningful because `timeout` is a plain user-supplied `uint256` in `SendParams` with no validation preventing `0`, and `0` is a natural "no timeout" value a caller or an integrating dApp/SDK default might pick (intentionally or by an uninitialized-variable bug), especially since `EvmHost.dispatch` already treats `0` specially as "infinite" for other purposes. Any subsequent, entirely realistic delivery failure (wrong recipient config, destination peer not yet registered, destination paused) then converts a normal bridging attempt into a permanent loss with no admin recourse, since the tokens are already burned (or locked in escrow with no other withdrawal path) and the timeout gate can never fire.

### Recommendation
Do not allow the "infinite timeout" sentinel (`timeout == 0`) to be usable in a way that permanently disables the *only* recovery path for a caller's own value. Options mirroring Sablier's fix:
- Enforce a maximum bound on `SendParams.timeout` in `HyperFungibleToken.send()`/`WrappedHyperFungibleToken.send()` / `_buildDispatchPost()` (reject `0` or values above a sane ceiling), so requests carrying user funds always have a real, bounded recovery timeout.
- Alternatively, add a grace-period fallback (e.g., allow the sender to self-timeout after N days regardless of `timeoutTimestamp`) so that a misconfigured/zero timeout does not translate into an unbounded freeze.

### Proof of Concept
1. Attacker/careless user calls `HyperFungibleToken.send(SendParams({ dest: X, to: Y, amount: A, timeout: 0, relayerFee: F, data: "" }))`. Tokens are burned; `EvmHost.dispatch` stores `timeoutTimestamp = 0` per [1](#0-0) .
2. `Message.timeout()` interprets this as `type(uint64).max` (no expiration) per [7](#0-6) .
3. Suppose the destination `to`/peer registration is wrong or the destination gateway is paused, so `onAccept()` on destination reverts (as demonstrated by `testOnAcceptRevertsUnsupportedChain` in [6](#0-5) ); the message is never successfully delivered.
4. Anyone tries to submit `handlePostRequestTimeouts` to reclaim the burned funds; the ISMP core handler checks `post.timed_out(state.timestamp())` per [3](#0-2)  and always reverts with `RequestTimeoutNotElapsed`, since `state.timestamp()` can never exceed `uint64.max`.
5. `onPostRequestTimeout()`, which is the only function that re-mints/unlocks the sender's funds, per [8](#0-7) , can never be called. Funds are permanently frozen with no clawback mechanism.

### Citations

**File:** evm/src/core/EvmHost.sol (L934-944)
```text
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
```

**File:** sdk/packages/core/contracts/libraries/Message.sol (L181-202)
```text
library Message {
    /**
     * @dev Calculates the absolute timeout value for a PostRequest
     */
    function timeout(PostRequest memory req) internal pure returns (uint64) {
        if (req.timeoutTimestamp == 0) {
            return type(uint64).max;
        } else {
            return req.timeoutTimestamp;
        }
    }

    /**
     * @dev Calculates the absolute timeout value for a GetRequest
     */
    function timeout(GetRequest memory req) internal pure returns (uint64) {
        if (req.timeoutTimestamp == 0) {
            return type(uint64).max;
        } else {
            return req.timeoutTimestamp;
        }
    }
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L75-81)
```rust
				if !post.timed_out(state.timestamp()) {
					Err(Error::RequestTimeoutNotElapsed {
						meta: post.into(),
						timeout_timestamp: post.timeout(),
						state_machine_time: state.timestamp(),
					})?
				}
```

**File:** modules/ismp/core/src/router.rs (L59-68)
```rust
impl PostRequest {
	/// Returns the timeout timestamp for a request
	pub fn timeout(&self) -> Duration {
		get_timeout(self.timeout_timestamp)
	}

	/// Returns true if the destination chain timestamp has exceeded the request timeout timestamp
	pub fn timed_out(&self, proof_timestamp: Duration) -> bool {
		proof_timestamp >= self.timeout()
	}
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L315-326)
```text
    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** evm/tests/foundry/HyperFungibleTokenTest.sol (L276-295)
```text
    function testOnAcceptRevertsUnsupportedChain() public {
        PostRequest memory request = PostRequest({
            source: StateMachine.evm(999), // unsupported
            dest: StateMachine.evm(1),
            nonce: 0,
            from: abi.encodePacked(address(0x1)),
            to: abi.encodePacked(address(hft)),
            timeoutTimestamp: 0,
            body: abi.encode(HyperFungibleToken.Message({
                from: abi.encodePacked(address(0x1)),
                to: abi.encodePacked(address(0x2)),
                amount: 1 ether,
                data: ""
            }))
        });

        vm.prank(address(host));
        vm.expectRevert(HyperFungibleToken.UnsupportedChain.selector);
        hft.onAccept(IncomingPostRequest({request: request, relayer: address(0)}));
    }
```
