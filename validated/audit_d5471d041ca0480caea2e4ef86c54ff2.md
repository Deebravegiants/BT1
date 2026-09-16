This confirms the mechanics needed to validate the analog. `EvmHost.dispatchIncoming` deletes the request receipt on a failed `onAccept` call so delivery is retryable "forever" rather than reverting the whole batch [1](#0-0) , but that only helps if the request can eventually time out. When `timeout` is `0`, both the Solidity and Substrate implementations treat the request as having an infinite timeout that "will never expire" [2](#0-1) [3](#0-2) , meaning there is no non-membership/timeout proof path ever available to unwind the send and refund the sender.

`WrappedHyperFungibleToken.onAccept` (and its upgradeable variant) delivers bridged funds by calling `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` directly to an address decoded from the cross-chain message body, with no try/catch [4](#0-3) . If `_underlying` is a blacklist-capable token like USDC and `beneficiary` is (or becomes) blacklisted, this `safeTransfer` reverts unconditionally, and since `dispatchIncoming` catches the failure and just deletes the receipt for retry [5](#0-4) , the message is retriable indefinitely but can never actually succeed.

### Title
Permanent freezing of bridged USDC funds when the beneficiary is blacklisted and `timeout == 0` in `WrappedHyperFungibleToken` - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.onAccept` pushes the underlying ERC20 (e.g. USDC) directly to a beneficiary address decoded from an untrusted, already-committed cross-chain message body via `IERC20(_underlying).safeTransfer(beneficiary, message.amount)`. If that beneficiary is blacklisted by the underlying token, the transfer reverts every time delivery is attempted. Because `send()` allows `timeout = 0` ("no timeout"), and `EvmHost`/pallet-ismp explicitly treat `timeoutTimestamp == 0` as "will never expire," there is no way to ever prove a non-membership/timeout to trigger the `onPostRequestTimeout` refund path on the source chain. The locked underlying tokens become permanently unrecoverable.

### Finding Description
`send()` locks the underlying token in the contract and dispatches a `DispatchPost` whose `timeout` field is attacker/user-controlled (`params.timeout`), and `0` is a documented valid value meaning "no timeout; messages will never expire" [6](#0-5) . On the EVM side, `EvmHost.dispatch` propagates a zero timeout as `timeoutTimestamp = 0` [7](#0-6) , and `Message.timeout()` maps a `0` timestamp to `type(uint64).max` [2](#0-1) ; the Substrate side does the analogous thing (`get_timeout` returns `Duration::MAX` for `timeout_timestamp == 0`) [3](#0-2) . `HandlerV2.handlePostRequestTimeouts`/pallet-ismp's timeout handler both require `request.timeout() <= state.timestamp` before a non-membership proof can even be checked [8](#0-7) , so a request with `timeoutTimestamp == 0` can never satisfy that condition and can never be refunded via `onPostRequestTimeout`.

On delivery, `WrappedHyperFungibleToken.onAccept` decodes `beneficiary` from the message body and unconditionally calls `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` with no fallback [4](#0-3) . If `beneficiary` is blacklisted for `_underlying` (realistically USDC, given this pattern mirrors the Sentiment V2 report), this call always reverts. `EvmHost.dispatchIncoming` catches this failure generically by deleting the just-written receipt and returning without reverting the whole relayer batch, explicitly "so that it can be retried" [9](#0-8) , but "retryable" here means it will fail identically forever, since the beneficiary address is fixed in the already-committed request body and cannot be changed.

The user's tokens are meanwhile locked in the `WrappedHyperFungibleToken` contract from the `send()` call, with no route to reclaim them: delivery can never succeed (permanent blacklist), and the `timeout == 0` request can never time out to trigger `onPostRequestTimeout`'s refund of the original sender.

### Impact Explanation
This results in permanent freezing of user funds: the locked underlying ERC20 (USDC) sits forever in the `WrappedHyperFungibleToken` contract, unreachable by the intended beneficiary (blacklisted, delivery always reverts) and unreachable by the original sender (no timeout mechanism exists for `timeout == 0` requests). No admin/governance function exists to force-release escrowed tokens for a specific stuck message. This matches the "permanent freezing of funds" impact bar.

### Likelihood Explanation
Likelihood is low but non-zero, matching the original Sentiment V2 M-12 rationale: USDC blacklist events are rare but real (legal/regulatory/AML actions, not solely on-chain hacks), and the attacker/victim only needs to specify `timeout = 0` (a normal, documented, expected usage pattern for "no timeout") and a beneficiary address that later becomes blacklisted, or is already blacklisted, to lock the funds with no recovery path. Unlike the original Sentiment report where the position needed to actively misbehave via `exec()` to get blacklisted, here the beneficiary can be any externally blacklisted address (e.g. a compromised account later sanctioned) with a self-inflicted or third-party origin, which is a normal, permissionless bridging flow through `send()`.

### Recommendation
- Disallow or discourage `timeout == 0` for the ERC20/underlying-token path of `WrappedHyperFungibleToken`, or enforce a maximum allowed timeout so that stuck deliveries can always eventually be refunded via `onPostRequestTimeout`.
- Wrap the `safeTransfer` to the beneficiary in a try/catch (mirroring the WETH branch's push/re-wrap fallback already used for native ETH transfers, e.g. `IWETH(_underlying).withdraw`/`deposit` fallback pattern at lines 316-321) so that a reverting transfer to a blacklisted beneficiary falls back to an escrow-and-claim mechanism (e.g. holding the tokens in the contract, redeemable by the beneficiary providing an alternate address, or by governance/admin recovery) instead of leaving `onAccept` unconditionally reverting forever.

### Proof of Concept
1. On the home chain, deploy `WrappedHyperFungibleToken` with `_underlying = USDC`.
2. Attacker/user calls `send({dest: remoteChain, to: beneficiaryAddr, amount: X, timeout: 0, relayerFee: 0, data: ""})`; USDC is locked into the contract via `safeTransferFrom` [10](#0-9) .
3. `beneficiaryAddr` becomes blacklisted by Circle (or is already blacklisted before delivery).
4. The relayer relays the message; `dispatchIncoming` calls `onAccept`, which calls `IERC20(_underlying).safeTransfer(beneficiaryAddr, X)`, which reverts due to the USDC blacklist; `dispatchIncoming` deletes the receipt and swallows the revert without reverting the batch tx.
5. Every subsequent relay attempt fails identically. Because `timeoutTimestamp == 0`, `HandlerV2.handlePostRequestTimeouts`'s check `request.timeout() > state.timestamp` (with `timeout()` resolving to `type(uint64).max`) always reverts with `MessageNotTimedOut`, so no timeout proof can ever be submitted to trigger the sender-side refund.
6. The `X` USDC locked in `WrappedHyperFungibleToken` in step 2 is permanently frozen with no recovery path for either the sender or the beneficiary.

### Citations

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

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

**File:** sdk/packages/core/contracts/libraries/Message.sol (L185-191)
```text
    function timeout(PostRequest memory req) internal pure returns (uint64) {
        if (req.timeoutTimestamp == 0) {
            return type(uint64).max;
        } else {
            return req.timeoutTimestamp;
        }
    }
```

**File:** modules/ismp/core/src/router.rs (L151-159)
```rust
/// Get the timeout in seconds
fn get_timeout(timeout_timestamp: u64) -> Duration {
	// zero timeout means no timeout.
	if timeout_timestamp == 0 {
		Duration::from_secs(u64::MAX)
	} else {
		Duration::from_secs(timeout_timestamp)
	}
}
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-273)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-324)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L42-46)
```text
| `to` | Receiving module/contract address on the destination chain. |
| `body` | Serialized byte representation of the message (to be decoded by the receiving contract). |
| `timeout` | Time in seconds for message validity eg 3600 for a timeout of 1 hour, or 0 for no timeout. ie Messages will never expire. If the timeout is set to a non-zero value, messages that have exceeded this timeout will be rejected on the destination and require user action (timeout message) to revert changes. |
| `fee` | Optional relayer fees in the fee token, this can also be set to zero if the application developers prefer to self-relay. |
| `payer` | The account that should receive a refund of the relayer fees if the request times out. |
```

**File:** evm/src/core/HandlerV2.sol (L267-270)
```text
        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();
```
