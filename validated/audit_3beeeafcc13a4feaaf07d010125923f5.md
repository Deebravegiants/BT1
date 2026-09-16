### Title
Cross-chain transfers to a zero-derived recipient address permanently burn tokens without minting on the destination - ([File: sdk/packages/core/contracts/apps/HyperFungibleToken.sol])

### Summary
`HyperFungibleToken.send()` burns tokens from the caller immediately and dispatches a cross-chain POST request; the destination's `onAccept` decodes the recipient and calls `_mint`. If the encoded 20-byte recipient decodes to `address(0)`, `_mint` reverts via OpenZeppelin's `ERC20InvalidReceiver` check, so the message can never be successfully delivered, while the source-side burn has already occurred.

### Finding Description
In `send()`, the caller's tokens are burned unconditionally before the cross-chain message is dispatched: [1](#0-0) 

On the destination chain, `onAccept` decodes the message body and extracts the recipient via `_toAddr`, then mints directly to it with no zero-address validation: [2](#0-1) 

`_toAddr` only validates the byte-length of the recipient encoding (must be 20 bytes) but performs no check that the decoded value is non-zero: [3](#0-2) 

Because the underlying `_mint` is OpenZeppelin's standard ERC20 `_mint`, which reverts when the target is `address(0)`, any incoming request whose `to` field decodes to the zero address will cause `onAccept` to revert every single time it is submitted (deterministically, regardless of which relayer delivers it) since the transaction always reverts before a receipt is recorded, so the relayer can retry indefinitely. If the outgoing message's `timeoutTimestamp` is left at `0` (as several test flows in this codebase do, e.g. `timeout: 0` in `BridgeTokenTest.t.sol`), the request is never eligible to time out, meaning `onPostRequestTimeout` (which is the only path that re-mints the burned amount back to the sender) is unreachable. The tokens burned at `send()` are then permanently unrecoverable — an exact analog of the reported `L1ECOBridge`/`ERC20Upgradeable._mint` issue, where minting to the zero address on delivery reverts and locks tokens that were already debited on the source side.

This same pattern is duplicated in `HyperFungibleTokenUpgradeable.sol`'s `onAccept`/`onPostRequestTimeout`, and any `WrappedHyperFungibleToken*` variant that follows the same `_toAddr`/`_mint` pattern is similarly exposed: [4](#0-3) 

### Impact Explanation
A user (or any relayer/dispatcher forwarding a crafted `to` value) can cause value to be burned on the source chain with the destination-side mint permanently reverting. If the `timeout` parameter is `0`, or if a griefer sets a zero timeout on their own transfer, the burned funds are irrecoverably lost with no compensating mint anywhere in the system — a permanent freezing/loss of user funds. This satisfies the "concrete... permanent freezing of funds" bar since the escrow-backed supply invariant (burn-here/mint-there) is broken: funds vanish from total supply without any path to reappear.

### Likelihood Explanation
This is trivially reachable from a single `send()` call with `to = abi.encodePacked(address(0))` and `timeout = 0`, which is exactly the parameterization used in several tests in this repository's own test suite (e.g., `bridge.send(... timeout: 0 ...)` in `BridgeTokenTest.t.sol`). No privileged role or governance action is needed; an ordinary user (or a UI bug, or a front-end address-parsing bug) can trigger this deterministically.

### Recommendation
Add an explicit zero-address check in `_toAddr` (or immediately after decoding the recipient in `onAccept`/`onPostRequestTimeout`) and revert with a clear error before calling `_mint`, so that malformed/zero-address destinations are rejected at the message-validation layer rather than relying on the ERC20 `_mint` revert, which — combined with a zero or short timeout — leaves the burned tokens unrecoverable. Additionally, consider disallowing a `timeout` of `0` in `send()` (or enforcing a minimum, non-zero timeout) so every dispatched transfer has a guaranteed refund path via `onPostRequestTimeout` if delivery cannot succeed.

### Proof of Concept
1. User calls `HyperFungibleToken.send(SendParams({dest: <destChain>, to: abi.encodePacked(address(0)), amount: 100 ether, timeout: 0, relayerFee: 0, data: ""}))`.
2. `send()` immediately burns `100 ether` from the caller and dispatches the POST request: [5](#0-4) 
3. Any relayer submits the proof to the destination chain; `onAccept` decodes `message.to` via `_toAddr` → `address(0)`, then calls `_mint(address(0), 100 ether)`, which reverts (`ERC20InvalidReceiver`).
4. Because the call reverts, no receipt is recorded on the destination host, so every future relayer submission of the same request reverts identically — the message can never be delivered.
5. Since `timeout` was `0`, `onPostRequestTimeout` can never be invoked for this request (no eligible timeout window), so the burned `100 ether` is permanently lost — the user's tokens are gone with no compensating mint anywhere in the system.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L271-282)
```text
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
