### Title
No incentive for relayers to submit permissionless timeout proofs, allowing bad debt/frozen relayer-fee escrow and stuck cross-chain funds to accumulate indefinitely - (File: evm/src/core/EvmHost.sol, modules/pallets/ismp/src/host.rs)

### Summary
`EvmHost.dispatchTimeOut(PostRequestTimeout)` and `pallet-ismp`'s `on_request_timeout` both refund the escrowed relayer fee to the *original payer* of the request, not to whoever submits the timeout proof and pays the gas/proving cost to trigger the refund. This is structurally the same incentive gap as the referenced Flatcoin finding: a necessary, protocol-health-preserving state transition (processing a timed-out request so escrowed value can be released/refunded) has zero economic reward for the caller who performs it, so rational relayers have no reason to do it, and stuck requests/escrow can pile up indefinitely.

### Finding Description
Hyperbridge's normal delivery path pays relayers for the work of relaying a message: on successful `handlePostRequests`/`handleGetResponses`, the fee escrowed at dispatch time is transferred to the relayer that performed the delivery [1](#0-0) .

However, the *timeout* path — which is also permissionless and callable by anyone — does not reward the caller at all. In `EvmHost.dispatchTimeOut(PostRequestTimeout)`, after the source application's `onPostRequestTimeout` callback succeeds, the escrowed fee is refunded to `meta.sender` (the original `payer` recorded at dispatch time), not to `msg.sender`/the relayer that submitted the timeout proof: [2](#0-1) 

The same design exists on the Polkadot/pallet-ismp side: `on_request_timeout` transfers the escrowed fee from `RELAYER_FEE_ACCOUNT` back to `leaf_meta.fee.payer`, again with no payment to the caller that produced/submitted the non-membership timeout proof: [3](#0-2) 

This is documented behavior, not an incidental bug: the docs explicitly describe `handlePostRequestTimeouts()` as "Permissionless (can be called by anyone)" with the effect "Refunds relayer fee to payer" [4](#0-3) , and the SDK docs confirm that timed-out cross-chain transfers are **not automatically refunded** — "The developer must initiate the timeout flow to recover the locked/burned tokens" [5](#0-4) . GET-request timeouts are even more explicit that there is no reward: "GET requests have no relayer fees, so no refunds occur" [6](#0-5) .

Just as the Flatcoin liquidator receives nothing (and eats gas costs) for liquidating a `settledMargin < 0` position, the party submitting a Hyperbridge timeout message receives nothing for the (nontrivial) cost of generating and submitting a non-membership/state proof plus paying destination gas — the entire benefit (the fee refund) accrues to a third party (the original payer), who has weaker technical capability/incentive to assemble cross-chain proofs than a professional relayer operator. Both `IntentGateway` cancellation-from-source (`DispatchGet` non-membership proof for `_filled[commitment]`) and `HyperFungibleToken`/`WrappedHyperFungibleToken` bridging rely on exactly this same unrewarded timeout-processing step to release locked/escrowed principal back to users.

### Impact Explanation
Because no economic actor is compensated for triggering the timeout path, there is a structural disincentive for permissionless relayers to ever process timeouts, especially for:
- Low-value or fee-less messages, where nobody bothers to generate consensus/state proofs purely out of altruism.
- Applications relying on the timeout callback to release escrowed principal (`IntentGateway` escrow refunds, `HyperFungibleToken` burn/lock reversal) — if the payer/user themselves lacks the technical means to self-relay (build MMR/state proofs, submit `handlePostRequestTimeouts`), their principal remains locked/frozen indefinitely even though it is nominally "recoverable."
- Escrowed relayer fees sitting in `RELAYER_FEE_ACCOUNT` (Polkadot side) or the `EvmHost` fee-token balance (EVM side) that never get released because nobody submits the timeout, representing stuck value that inflates the appearance of protocol-held funds without being truly available.

This is a Medium/High-severity freezing-of-funds risk: user principal and escrowed fees can become permanently or indefinitely locked in a state that requires an altruistic, unpaid third party to unlock, with no protocol-level guarantee that anyone will do so.

### Likelihood Explanation
Likelihood is credible: every ordinary user/relayer economic behavior modeled elsewhere in Hyperbridge (the entire fee-accumulation/reward system in `pallet-ismp-relayer`, the `outbound-request-incentivization` effort) is premised on relayers being profit-driven and only acting when compensated [7](#0-6) . The same profit-driven relayer network has zero reason to spend gas/proof-generation effort on the timeout path, since it is explicitly the payer, not the deliverer, who is compensated. This condition triggers automatically any time a message goes unfulfilled past its `timeoutTimestamp` — a routine occurrence (destination congestion, liveness failures, relayer race losses) — not an edge case requiring adversarial conditions.

### Recommendation
Introduce a timeout-processing incentive symmetric to the delivery-reward path: e.g., split the escrowed relayer fee between the timeout submitter (gas/proof cost + margin) and the original payer, or let applications configure a dedicated "timeout relayer fee" separate from the delivery fee. This mirrors the fix pattern Hyperbridge already uses for other previously-unincentivized flows (see `OutboundRequestDeliveryReward` in `modules/pallets/relayer/src/outbound_request.rs`), and would ensure timed-out requests — and the escrow/principal locked behind them — are promptly and reliably processed rather than depending on altruism or the payer's own technical capability.

### Proof of Concept
1. App `A` dispatches a `DispatchPost` with `fee = F`, `payer = A`, `timeout = T` via `EvmHost.dispatch` [8](#0-7) .
2. No relayer ever delivers the message before `timeoutTimestamp` (e.g., destination congestion, relayer prioritizes higher-fee messages).
3. Timeout is now processable via `HandlerV2`/`IHandler.handlePostRequestTimeouts`, which is permissionless [4](#0-3) .
4. A relayer who is capable of submitting this timeout would need to: generate a non-membership state proof, pay destination/source gas, and submit the transaction — for **zero reward**, since `dispatchTimeOut` refunds `F` to `meta.sender` (=`A`), not to the caller [2](#0-1) .
5. Rational relayers skip this transaction entirely (negative expected value). If `A` (e.g., a bridging user who burned/locked tokens via `HyperFungibleToken`) cannot self-relay (lacks SDK tooling, technical sophistication, or is unaware), the burned/locked principal and the escrowed fee `F` remain stuck with no timeline for recovery — confirmed by the docs stating recovery is not automatic and "the developer must initiate the timeout flow" [5](#0-4) .

### Citations

**File:** evm/src/core/EvmHost.sol (L841-847)
```text
        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L885-906)
```text
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L921-948)
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
```

**File:** modules/pallets/ismp/src/host.rs (L322-335)
```rust
	fn on_request_timeout(&self, _req: &Request, meta: Vec<u8>) -> Result<(), Error> {
		let leaf_meta = RequestMetadata::<T>::decode(&mut &*meta)
			.map_err(|_| Error::Custom("Failed to decode leaf metadata".to_string()))?;
		if leaf_meta.fee.fee > Zero::zero() {
			T::Currency::transfer(
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				&leaf_meta.fee.payer,
				leaf_meta.fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| Error::Custom(format!("Failed to refund relayer fee: {err:?}")))?;
		}
		Ok(())
	}
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L121-154)
```text
### handlePostRequestTimeouts()

Processes timed-out POST requests and triggers refunds.

```solidity lineNumbers
function handlePostRequestTimeouts(
    IHost host,
    PostRequestTimeoutMessage calldata message
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `IHost` | The IHost contract |
| `message` | `PostRequestTimeoutMessage` | Struct containing timeout proof and requests |

**Access:** Permissionless (can be called by anyone)

**Process:**
1. Verifies timeout proof
2. For each request:
   - Validates timeout timestamp has passed
   - Calls `onPostRequestTimeout()` on source application
   - Refunds relayer fee to payer (only if callback succeeds)

**Important:**
- Application timeout callback is called **before** refund
- If callback reverts, no refund occurs
- Timeout can be resubmitted until callback succeeds

**Reverts:**
- `MessageNotTimedOut()` - Timeout period not elapsed
- `UnknownMessage()` - Request not found

```

**File:** docs/content/developers/sdk/hyper-fungible-token.mdx (L247-260)
```text
## Handling Timeouts

If a cross-chain transfer is not delivered before its `timeout` expires, the tokens are not automatically refunded. The developer must initiate the timeout flow to recover the locked/burned tokens.

The bridge generator's status stream will detect when a request has timed out:

```typescript lineNumbers title="bridge.ts" icon=typescript
if (step.type === "status") {
  if (step.status === "TIMED_OUT") {
    console.log("Request timed out — initiate timeout recovery")
    break
  }
}
```
```

**File:** docs/content/developers/evm/api/ihost.mdx (L372-393)
```text
### dispatchTimeOut(GetRequestTimeout)

Dispatches a timed-out GET request to the source application's `onGetTimeout()` callback.

```solidity lineNumbers
function dispatchTimeOut(
    GetRequestTimeout memory timeout, 
    FeeMetadata memory meta, 
    bytes32 commitment
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `timeout` | `GetRequestTimeout` | The timed-out GET request bundled with the relayer that submitted the timeout proof |
| `meta` | `FeeMetadata` | Fee metadata |
| `commitment` | `bytes32` | Request commitment hash |

**Access:** Restricted to handler

**Note:** GET requests have no relayer fees, so no refunds occur.

```

**File:** docs/outbound-request-incentivization.md (L7-21)
```markdown
## The problem

A regular cross-chain message that flows *through* hyperbridge has a fee attached at origin (the source chain transfers `fee.payer → RELAYER_FEE_ACCOUNT` and records `RequestPayments[commitment]` in pallet-hyperbridge's child trie). When a relayer delivers and the destination receipt lands back on hyperbridge, the existing `accumulate_fees` flow credits that fee to the relayer. That whole pipeline assumes a *user* paid at origin.

But hyperbridge itself originates requests too: host parameter propagation, host-executive updates, intents-coprocessor responses, token-governor messages, the relayer pallet's withdrawal request. Today these all dispatch with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` (see `modules/pallets/host-executive/src/lib.rs:228`, `modules/pallets/intents-coprocessor/src/lib.rs:486`, `modules/pallets/relayer/src/lib.rs:638`, and `modules/pallets/token-governor/src/impls.rs`). Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism.

## The shape of the solution

The issue creator's preferred shape ([comment 4428807013](https://github.com/polytope-labs/hyperbridge/issues/532#issuecomment-4428807013)): use `pallet-relayer` to pay BRIDGE to whoever proves they delivered a hyperbridge-originated request. The messaging task in the tesseract relayer submits the claim.

Not every pallet on hyperbridge that dispatches a request is in scope. `pallet_ismp::child_trie::RequestCommitments` ends up holding commitments for every successful dispatch via `IsmpDispatcher`, which includes both the system messages we want to incentivize (host-executive, intents-coprocessor, token-governor, the relayer pallet's withdrawal path, future modules like bandwidth) and any other pallet that ends up dispatching from hyperbridge. The reward storage is therefore keyed by `source_module_id` and only modules with a non-zero reward are eligible. The `module_id` is the `from` field on the `PostRequest`, which each pallet sets to its unique module identifier. A module with zero reward is treated as not on the allowlist and rejected before any state proof verification runs.

This is structurally identical to the existing `claim_outbound_consensus_delivery_reward` (see `modules/pallets/relayer/src/outbound_consensus.rs`) on the consensus side. The request claim lives in its own `modules/pallets/relayer/src/outbound_request.rs` module that mirrors it: swap "consensus rotation delivered" for "request delivered," key the reward storage by `module_id`, and have the relayer ship the full `PostRequest` in the claim so the pallet can hash it on chain.

No changes to pallet-hyperbridge or to any of the system-message dispatch sites. The reward is decoupled from the dispatch path and paid out at claim time against a destination state proof.
```
