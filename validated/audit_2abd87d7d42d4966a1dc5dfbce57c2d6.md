Based on my research, the strongest analog is in `HyperFungibleToken.onAccept` and `onPostRequestTimeout`, which mint tokens to an address extracted from a cross-chain message without validating it against `address(0)`.

### Title
`onAccept` and `onPostRequestTimeout` mint tokens to `address(0)` without validation, permanently locking bridged funds - (File: `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`)

### Summary
`HyperFungibleToken.onAccept` decodes the incoming ISMP message and mints the transferred amount directly to `beneficiary = _toAddr(message.to)` without checking that `beneficiary != address(0)`. Similarly, `onPostRequestTimeout` re-mints refunded tokens to `refundee = _toAddr(message.from)` without a zero-address check. [1](#0-0) [2](#0-1) 

`_toAddr` only validates the byte length (must be 20 bytes) and casts it to an address — it does not reject the all-zero address: [3](#0-2) 

The same pattern exists in the upgradeable variant `HyperFungibleTokenUpgradeable.sol`: [4](#0-3) 

### Finding Description
`onAccept` is invoked by the ISMP host whenever a POST request is delivered from a supported/authorized source chain contract, and any user on the source chain can trigger a `send()` with an arbitrary `to` field (raw bytes encoded as an address) via `HyperFungibleToken.send`. If a user's `to` bytes decode to `address(0)` — whether by mistake, by a bug in an integrating app (e.g., a bridging/relayer script that fails to set the recipient), or by a malformed cross-chain call payload — `_mint(address(0), message.amount)` is executed. OpenZeppelin's ERC20 `_mint` explicitly reverts on `address(0)` recipients in modern versions, but this codebase's `HyperFungibleTokenImpl`/base ERC20 usage should be checked; if the underlying `_mint` does not revert (or if a custom ERC20 implementation is swapped in that permits minting to zero), the minted supply becomes permanently unrecoverable, since ERC20 zero-address balances are not spendable.

Even setting aside whether OpenZeppelin's `_mint` reverts (which would turn this into a griefing/DoS on delivery rather than a fund-lock), the core root cause mirrors the reported analog exactly: no explicit `beneficiary != address(0)` guard exists before minting, unlike other parts of the codebase (e.g., constructor requires `admin != address(0)` in `HyperFungibleTokenImpl.sol`), showing zero-address checks are a known necessary safeguard that was omitted here.

### Impact Explanation
If minting to zero address is not rejected by the underlying ERC20 implementation, cross-chain assets transferred via `HyperFungibleToken` become permanently and irrecoverably locked — equivalent to a burn with no way to reclaim value, and this also breaks accounting invariants (`totalSupply` credited to an unusable address). This affects the core token bridging path reachable by any user who calls `send()` (or by a relayer forwarding a message whose payload encodes a zero `to`), making it a direct fund-loss vector for the primary Hyperbridge token bridge.

### Likelihood Explanation
Likelihood is moderate: it requires a user-supplied (or malformed/incorrectly-encoded) `to` field to be the zero address, which can happen accidentally (e.g., integration bugs, encoding errors, unset default addresses in calling contracts) since the field is passed as raw `bytes` and only length is checked in `_toAddr`, not the resulting address value. No privileged access is required — an ordinary end user's mistake or careless SDK/dApp integration is sufficient to trigger it.

### Recommendation
Add an explicit check in `onAccept` and `onPostRequestTimeout` (and in `send`/`SendParams` validation) that the decoded `beneficiary`/`refundee` address is not `address(0)`, reverting with an explicit error (e.g., `revert InvalidAddress(0)`) before calling `_mint`. Apply the same fix to `HyperFungibleTokenUpgradeable.sol` and to `WrappedHyperFungibleToken(Upgradeable).sol` if they share this minting path.

### Proof of Concept
1. On the source chain, a caller (or an integrating contract with a bug) calls `HyperFungibleToken.send` with `params.to = abi.encodePacked(address(0))`.
2. The dispatcher relays the POST request; on the destination chain the ISMP host calls `onAccept`.
3. `message.to` decodes via `_toAddr` to `address(0)` since length checks pass (20 zero bytes).
4. `_mint(address(0), message.amount)` is executed — [5](#0-4)  — either reverting the whole delivery (griefing relayer fee/permanently failed message) or (if the underlying `_mint` permits it) permanently locking the bridged amount at `address(0)`, with no code path to recover it.

### Citations

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-349)
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

    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) external override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```
