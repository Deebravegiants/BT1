## Title
Cross-chain token transfer to `address(0)` permanently burns user funds with no recovery path - (`sdk/packages/core/contracts/apps/HyperFungibleToken.sol`)

### Summary
`HyperFungibleToken.send()` lets any token holder burn their balance and dispatch a cross-chain transfer to an arbitrary recipient encoded as raw `bytes`. Neither `send()` nor the receiving side's `onAccept()`/`_toAddr()` validate that the decoded recipient is non-zero. A user (or SDK caller) who mistakenly supplies `to = address(0)` burns their tokens on the source chain and the destination chain then mints the equivalent supply to `address(0)`, permanently destroying the value with no way to recover it — mirroring the analog report's "specific parameters cause total loss of assets" bug class.

### Finding Description
`send()` immediately burns the caller's balance and builds the outgoing message with the caller-supplied `params.to` unchecked: [1](#0-0) [2](#0-1) 

On the destination chain, `onAccept` decodes `message.to` via `_toAddr` and mints directly to it, again with no zero-address check: [3](#0-2) [4](#0-3) 

`_toAddr` only validates the byte-length is 20; it never rejects the zero address: [4](#0-3) 

Because the source-chain burn happens unconditionally in `send()` before dispatch, and the destination-chain `_mint` has no guard either, a `to = address(0)` transfer irreversibly destroys the transferred amount: it is burned on the source and minted to an address nobody controls on the destination (functionally equivalent to a second burn). The identical unguarded pattern also exists in the upgradeable variant: [5](#0-4) [6](#0-5) 

This is exactly analogous to the referenced Gearbox `CreditManager` bug: a caller-supplied recipient parameter reachable by an unprivileged, permissionless actor (any token holder acting as a "token bridger") that, if left as the zero address, causes unconditional and unrecoverable loss of funds, with the same recommended fix (reject `to == address(0)`).

### Impact Explanation
Any amount sent with a zero/malformed recipient is burned on the source chain and then minted to `address(0)` (an address with no private key) on the destination chain. The funds are permanently unrecoverable — a direct, concrete loss-of-funds condition, matching the "permanent freezing of funds" acceptance criterion. Every deployment of `HyperFungibleToken`/`HyperFungibleTokenUpgradeable` (including the canonical `BridgeToken`, which inherits `onAccept` from the base and does not add such a check) is affected.

### Likelihood Explanation
The trigger requires only a single call to the public, unprivileged `send()` function with a malformed `to` parameter (e.g., a zero address, or in SDK integrations a truncated/mis-encoded recipient that decodes to all zero bytes). No special privileges, timing, or race conditions are needed — a single mistaken or buggy client-side call is sufficient, exactly as in the analog report where the trigger was a single miscalled function.

### Recommendation
Add an explicit check in `send()`/`_buildDispatchPost()` that the decoded `params.to` is not the zero address before burning and dispatching, and add a defensive check in `onAccept()`/`_toAddr()` that reverts (or refuses to mint) rather than minting to `address(0)`. Apply the same fix to `HyperFungibleTokenUpgradeable.sol` and any inheriting contracts (e.g. `BridgeToken`).

### Proof of Concept
1. Caller holds `amount` tokens of `HyperFungibleToken` on chain A and calls:
   `send(SendParams({dest: chainB, to: abi.encodePacked(address(0)), amount: amount, timeout: t, relayerFee: fee, data: ""}))`.
2. `send()` executes `_burn(msg.sender, amount)` unconditionally, then dispatches the ISMP POST request with `to = address(0)` encoded in the message body.
3. Once delivered, chain B's `onAccept()` decodes `beneficiary = _toAddr(message.to) == address(0)` and calls `_mint(address(0), amount)`.
4. The `amount` is now permanently destroyed: burned on chain A, minted to an uncontrollable address on chain B, with no code path to reclaim it.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L241-256)
```text
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-266)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L298-301)
```text

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
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

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L361-367)
```text
    /// @notice Extracts an address from the first 20 bytes of a bytes memory value
    function _toAddr(bytes memory b) internal pure returns (address addr) {
        if (b.length != 20) revert InvalidAddress(b.length);
        // casting to 'bytes20' is safe because we already checked length
        // forge-lint: disable-next-line(unsafe-typecast)
        return address(bytes20(b));
    }
```
