### Title
Owner-controlled `pause()` blocks delivery/refund of already-committed cross-chain transfers in `HyperFungibleToken` / `WrappedHyperFungibleToken` / `HyperbridgeLzEndpoint` - (File: `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`)

### Summary
`HyperFungibleToken`, `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`, `WrappedHyperFungibleTokenUpgradeable`, and `HyperbridgeLzEndpoint` all gate `onAccept` (destination-side settlement/mint of an already-burned/locked transfer) and, for the fungible-token contracts, `onPostRequestTimeout` (refund of an already-burned transfer that timed out) behind `whenNotPaused`, with `pause()`/`unpause()` callable solely by `onlyOwner`. This mirrors the Sense `Divider` finding: the owner can pause not only new/"inbound" user actions (`send`) but also the "outbound" settlement of value a user is already unconditionally owed (mint on delivery, or refund on timeout), which is exactly the anti-pattern the referenced report calls out.

### Finding Description
- `send()` burns the caller's tokens and dispatches a POST request; it is correctly gated by `whenNotPaused` since it's a new, avoidable user action: [1](#0-0) 
- `onAccept`, which mints tokens to the recipient once a transfer has already been burned on the source chain and delivered via proof, is also gated by `whenNotPaused`: [2](#0-1) 
- `onPostRequestTimeout`, which re-mints tokens back to the original sender as a refund after a send has timed out, is likewise gated by `whenNotPaused`: [3](#0-2) 
- The same pattern repeats in the upgradeable and wrapped variants: [4](#0-3) [5](#0-4) [6](#0-5) 
- `HyperbridgeLzEndpoint.onAccept`, which delivers an inbound LZ message (already committed on the source chain) to the destination `OApp`, is also `whenNotPaused`: [7](#0-6) 
- Both `pause()`/`unpause()` are `onlyOwner` with no time bound or dispute-resolution guard, so a single key fully controls whether already-owed value can be settled: [8](#0-7) 

When these callbacks revert (because paused), `EvmHost.dispatchIncoming`/`dispatchTimeOut` treat the revert as a "not yet delivered" outcome and roll back the receipt/commitment so the message can be retried later — the delivery is not consumed on failure: [9](#0-8) [10](#0-9) 

### Impact Explanation
Because delivery is retryable once unpaused, this is not a permanent loss of funds, but it is a genuine centralization/availability risk consistent with a Medium severity: the token owner unilaterally decides, with a single `pause()` call, whether users who have already burned/locked their tokens on the source chain can receive their minted tokens or their timeout refund on the destination chain. Unlike pausing `send` (which only prevents new user-initiated risk), pausing `onAccept`/`onPostRequestTimeout` withholds value a user is already unconditionally entitled to, for an indefinite period fully at the owner's discretion — the classic "outbound should not be pausable" centralization concern from the referenced report.

### Likelihood Explanation
The `onlyOwner` role is trusted but not decentralized, and pausing is a single, cheap transaction with no time lock, multisig delay requirement, or governance path enforced at the contract level. Any owner (or a compromised owner key) can trigger this at will, and it's a realistic action during incident response or governance disputes, which is precisely when users most need settlement/refunds to go through.

### Recommendation
Split the pause flag so `send()` (new outbound initiation) can be halted independently from settlement of already-committed transfers. Remove `whenNotPaused` from `onAccept` and `onPostRequestTimeout` (and the LZ endpoint's `onAccept`), or add a separate, more restrictive/limited pause mechanism (e.g., time-bounded, multisig/governance-gated) specifically for those functions, so that once a transfer has been irrevocably burned/escrowed on the source chain, its destination-side mint or timeout refund cannot be withheld indefinitely by a single owner key.

### Proof of Concept
1. User calls `HyperFungibleToken.send(...)`, burning `amount` tokens and dispatching a `PostRequest` to the destination chain.
2. Before the message is relayed/delivered, the token owner calls `pause()`.
3. The relayer submits the proof; `EvmHost.dispatchIncoming` calls `onAccept`, which reverts due to `whenNotPaused` — the mint never happens, and (per `dispatchIncoming`'s retry logic) the receipt is rolled back.
4. If the message instead times out, `EvmHost.dispatchTimeOut` calls `onPostRequestTimeout`, which also reverts due to `whenNotPaused` — the user's refund mint never happens.
5. The user's tokens remain burned with no mint and no refund until the owner chooses to `unpause()`, entirely at the owner's discretion and with no on-chain time bound.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L211-223)
```text
     * @dev Only callable by the contract owner
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @notice Unpauses all cross-chain operations
     * @dev Only callable by the contract owner
     */
    function unpause() external onlyOwner {
        _unpause();
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L316-326)
```text
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-300)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
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

    /**
     * @notice Handles incoming cross-chain token transfer messages
     * @dev Called by the ISMP host when a POST request is received. Verifies the source
     * address matches the configured contract for that chain, then transfers the underlying
     * ERC20 to the recipient. If calldata is present, executes it via the CallDispatcher.
     * @param incoming The incoming POST request containing the token transfer message
     */
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-330)
```text
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
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

    /**
     * @notice Handles incoming cross-chain token transfer messages
     * @dev Called by the ISMP host when a POST request is received. Verifies the source
     * address matches the configured contract for that chain, then transfers the underlying
     * ERC20 to the recipient. If calldata is present, executes it via the CallDispatcher.
     * @param incoming The incoming POST request containing the token transfer message
     */
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L355-356)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;
```

**File:** evm/src/core/EvmHost.sol (L805-818)
```text
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
