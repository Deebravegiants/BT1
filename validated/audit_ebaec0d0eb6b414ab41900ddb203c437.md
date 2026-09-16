## Analog Found

### Title
`HyperFungibleToken.send()` performs no zero-address check on the recipient, permanently burning tokens with no way to recover them - ([File: sdk/packages/core/contracts/apps/HyperFungibleToken.sol])

### Summary
`HyperFungibleToken.send()` lets any token holder burn their balance and dispatch a cross-chain transfer message specifying an arbitrary `params.to` recipient, with no validation that the encoded recipient address is non-zero. If a caller supplies the zero address (or any other un-spendable/burn address) as `params.to`, the tokens are burned on the source chain and, on delivery, minted to `address(0)` on the destination chain — a state from which they can never be recovered by anyone.

### Finding Description
`send()` immediately burns the caller's tokens and builds/dispatches a cross-chain message before any validation of the destination recipient: [1](#0-0) 

The recipient is encoded from `params.to` into the `Message.to` field via `_buildDispatchPost`, again with no zero-value check — only the destination chain existing (`_supportedChains[params.dest]`) is validated: [2](#0-1) 

On the destination chain, `onAccept` decodes the message and mints directly to the decoded beneficiary, again with no non-zero check — `_toAddr` only validates the byte length (20 bytes), not the value: [3](#0-2) [4](#0-3) 

This mirrors the reported `AccountFacet.depositFor()` bug class exactly: an unprivileged user-initiated action (a token transfer/deposit) accepts an arbitrary destination address with no zero-address guard, and once the funds move (burn on source + mint-to-zero on destination), they are permanently and irrecoverably lost — nobody controls the private key for `address(0)`, and there is no analog of a timeout/refund path for a message that was *successfully delivered* to a zero recipient (only `onPostRequestTimeout`, for undelivered messages, re-mints to the sender).

### Impact Explanation
Any user error (fat-fingered address, wrong byte-padding/encoding of the 20-byte address, integration bug in a caller/dApp) results in an irreversible loss of the user's full bridged balance for that transfer. Because `BridgeToken` (nexus-backed) and any third-party token built from this shared `HyperFungibleToken` library inherit this same `send()`/`onAccept()` path, the class of loss is systemic across all deployments of the library, not a single contract bug. This satisfies "permanent freezing/loss of funds" from a single unprivileged transaction.

### Likelihood Explanation
Likelihood is driven entirely by user/integrator error rather than malicious action, but it is realistic: `params.to` is a raw `bytes` recipient field (per the `SendParams`/`Message` encoding used for cross-chain compatibility), so incorrect padding, decoding, or a zeroed placeholder passed by an integrating frontend/contract will silently pass validation and only fail at the point of no return (burn already executed on source). No special conditions or privileges are needed to trigger it — a single `send()` call is sufficient.

### Recommendation
Add an explicit check in `send()` (and/or `_buildDispatchPost`) that the decoded 20-byte recipient inside `params.to` is not the zero address before burning and dispatching, e.g. reject if `_toAddr(params.to) == address(0)`. Optionally also guard `onAccept`/`onPostRequestTimeout`'s `_toAddr` result so that even a message that somehow encodes a zero beneficiary is rejected/refunded rather than minted to `address(0)`.

### Proof of Concept
1. User calls `send(SendParams{ dest: <validChain>, to: abi.encodePacked(address(0)), amount: 1000, ... })` on a `HyperFungibleToken`/`BridgeToken` deployment.
2. `send()` executes `_burn(msg.sender, 1000)` unconditionally, then dispatches the ISMP POST request containing `Message.to = address(0)` bytes. [5](#0-4) 
3. On delivery, the destination host calls `onAccept`, which decodes `message.to` via `_toAddr` (passes the length check since it's still 20 bytes) and calls `_mint(address(0), 1000)`. [6](#0-5) 
4. The 1000 tokens are now minted to `address(0)` on the destination chain — permanently unspendable — while the source-chain supply was already burned, i.e., total value is destroyed with no route to recovery (unlike the timeout path, which only re-mints to the sender for undelivered messages).

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
