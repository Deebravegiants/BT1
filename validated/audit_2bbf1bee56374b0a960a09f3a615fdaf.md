## Title
Missing recipient validation in `HyperFungibleToken.send()` permanently freezes bridged funds when combined with a zero/no-timeout request - ([File: sdk/packages/core/contracts/apps/HyperFungibleToken.sol])

### Summary
`HyperFungibleToken.send()` burns the caller's tokens and dispatches a cross-chain POST request without validating that `params.to` decodes to a usable, non-zero recipient address. If the destination `to` is malformed (wrong length) or is the zero address, delivery on the destination chain will deterministically revert forever in `onAccept`. Because the ISMP protocol treats `timeout == 0` as "never times out," a request dispatched with `timeout: 0` and a bad `to` can neither be delivered nor recovered via the timeout/refund path, permanently freezing the burned tokens — the same class of bug as the referenced report (minting/burning proceeds without validating the receiver, and no safeguard exists for the degenerate case).

### Finding Description
`send()` burns tokens from `msg.sender` and immediately dispatches the request, with no check that `params.to` is a valid 20-byte, non-zero address: [1](#0-0) 

The only validation of the recipient happens later, on the destination chain, inside `onAccept`, which decodes `message.to` via `_toAddr` and mints to it: [2](#0-1) 

`_toAddr` reverts if the byte length isn't exactly 20, but does not reject the zero address: [3](#0-2) 

If `beneficiary == address(0)` (or `_toAddr` reverts on malformed length), `_mint` reverts (OpenZeppelin's ERC20 rejects minting to the zero address), so `onAccept` reverts deterministically for every relayer delivery attempt of that exact request. Since the request body/commitment is fixed, this failure is not transient — no future call will ever succeed.

Normally an undeliverable request can be recovered via `onPostRequestTimeout`, which re-mints the burned amount back to the sender: [4](#0-3) 

However, `SendParams.timeout` is fully attacker/user-controlled and unvalidated in `_buildDispatchPost`: [5](#0-4) 

Both the EVM dispatcher and the Substrate dispatcher treat `timeout == 0` as "no timeout" — the request can never expire and thus can never be submitted for a timeout refund: [6](#0-5) [7](#0-6) [8](#0-7) 

Combining these facts: a transfer dispatched with `timeout: 0` and a malformed/zero `to` burns the sender's tokens on the source chain, can never be minted on the destination (deterministic revert), and can never be refunded via timeout (the request never expires). The tokens are permanently and unrecoverably lost.

### Impact Explanation
This is a concrete, permanent freezing of user funds reachable by a single unprivileged transaction to the token bridge's `send()` function — no privileged role, governance, or malicious operator is required. The affected contract is deployed as `HyperFungibleToken` and its subclasses (e.g. `BridgeToken`) on every remote chain that doesn't hold native token supply, so the impact applies broadly across the token-bridging surface described in the docs.

### Likelihood Explanation
Likelihood is High for accidental loss (a wallet/integrator bug that miscomputes/truncates the `to` bytes, or a naive UI default of `timeout: 0` for "no timeout" as explicitly suggested in the docs) and remains reachable for a deliberate self-inflicted DoS test since no on-chain guard prevents it. The docs themselves describe `timeout: 0` as a normal, supported option ("0 for no timeout... Messages will never expire"), making the vulnerable combination easy to hit inadvertently.

### Recommendation
- In `HyperFungibleToken.send()` / `_buildDispatchPost`, validate `params.to` decodes to a well-formed, non-zero recipient address (length == 20 for EVM destinations, non-zero bytes) before burning tokens and dispatching.
- Consider disallowing `timeout == 0` for token-transfer messages, or enforce a maximum/minimum bound, so every dispatched transfer is guaranteed to be recoverable via `onPostRequestTimeout` if delivery permanently fails.
- Alternatively, have `onAccept` catch a failed mint (e.g., zero-address or malformed recipient) and fall back to a recoverable state instead of an unconditional revert, though restricting invalid input at the source (`send`) is the most robust fix.

### Proof of Concept
1. User calls `HyperFungibleToken.send(SendParams{ dest: <chain>, to: abi.encodePacked(address(0)), amount: X, timeout: 0, relayerFee: 0, data: "" })`.
2. `send()` executes `_burn(msg.sender, X)` and dispatches a `PostRequest` with `timeoutTimestamp = 0` (per `EvmHost.dispatch`/pallet dispatcher, `timeout == 0` maps to `timeoutTimestamp = 0`).
3. Any relayer submits the request; on the destination chain `onAccept` decodes `message.to` to `address(0)` via `_toAddr` and calls `_mint(address(0), X)`, which reverts every time — the request can never be delivered.
4. No one can submit a timeout message because `Message.timeout()`/`get_timeout()` treats `timeoutTimestamp == 0` as `type(uint64).max` / `Duration::MAX`, so the request is never considered "timed out."
5. The `X` tokens burned in step 2 are permanently unrecoverable.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L237-256)
```text
    function _buildDispatchPost(SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-282)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L321-326)
```text
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L328-334)
```text
    /// @notice Extracts an address from the first 20 bytes of a bytes memory value
    function _toAddr(bytes memory b) internal pure returns (address addr) {
        if (b.length != 20) revert InvalidAddress(b.length);
        // casting to 'bytes20' is safe because we already checked length
        // forge-lint: disable-next-line(unsafe-typecast)
        return address(bytes20(b));
    }
```

**File:** evm/src/core/EvmHost.sol (L933-944)
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
