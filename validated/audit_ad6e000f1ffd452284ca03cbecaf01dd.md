Confirmed: `timeout == 0` means "no timeout, message never expires" (documented explicitly and implemented consistently in `evm/src/core/EvmHost.sol` dispatch functions, `modules/pallets/ismp/src/dispatcher.rs`, and `sdk/packages/core/contracts/libraries/Message.sol`). This makes the blacklist analog a real, unrecoverable freeze rather than a temporary one.

### Title
Cross-chain token transfer to a blacklisted (e.g. USDC) recipient permanently locks user funds when dispatched with `timeout = 0` - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` locks a user's underlying ERC20 (which can be a blacklist-capable token such as USDC) and dispatches a POST request to mint/release the wrapped representation to a beneficiary on the destination chain. `onAccept()` on the destination pushes the underlying token directly to the `beneficiary` via `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` [1](#0-0) . If the beneficiary is blacklisted by the underlying token (e.g. USDC), this transfer reverts.

### Finding Description
`EvmHost.dispatchIncoming(PostRequest, ...)` invokes `onAccept` via a low-level `.call`, and on failure only deletes the request receipt "so that it can be retried" [2](#0-1) . This is designed to let a relayer retry delivery later (e.g. after temporary reverts). However, if the failure cause is *permanent* — the beneficiary is blacklisted from the underlying token — every retry attempt will fail identically forever; the request can never be delivered.

The user's only path to recover funds locked on the source chain is a timeout: `onPostRequestTimeout` refunds the locked underlying token back to the original sender [3](#0-2) . But `timeout = 0` is explicitly documented and implemented as "no timeout... messages will never expire" [4](#0-3) [5](#0-4) . A user (or a front-end/integration) can call `send()` with `params.timeout = 0`, and if that beneficiary is (or later becomes) blacklisted on the underlying token, the locked tokens are **permanently and irrecoverably frozen** in the `WrappedHyperFungibleToken` contract: delivery can never succeed (permanent revert), and there is no timeout path to refund since the request never expires.

The same pattern applies to `HyperFungibleTokenUpgradeable`/`HyperFungibleToken` mint-based variants where recovery instead depends on re-minting on timeout [6](#0-5) , and to `WrappedHyperFungibleTokenUpgradeable.onAccept` [7](#0-6)  — all share the same permanent-delivery-failure + no-expiry combination.

### Impact Explanation
Funds transferred cross-chain via `WrappedHyperFungibleToken`/`HyperFungibleToken` with `timeout = 0` targeting a beneficiary who is (or becomes) blacklisted by the underlying token become permanently unrecoverable: they cannot be delivered (delivery reverts indefinitely) and cannot be refunded (no timeout ever fires). This is a permanent freezing of user funds, meeting the Medium/High bar for concrete permanent loss of funds via a single ordinary user-initiated `send()` transaction.

### Likelihood Explanation
Reaching this requires only a normal unprivileged `send()` call: `timeout=0` is a valid, documented parameter choice ("no timeout"), and USDC-style blacklisting of a destination address is a realistic external event that can occur at any time before or after dispatch (including cases where the token contract itself decides to blacklist an address later, independent of the sender's intent). No privileged role or malicious behavior is needed — only a normal deposit combined with a foreseeable business-logic condition on a widely used token (USDC).

### Recommendation
- Do not treat `timeout = 0` as infinite for `HyperFungibleToken`/`WrappedHyperFungibleToken` sends, or enforce a protocol-level maximum timeout so refund logic is always eventually reachable.
- In `onAccept`, wrap the underlying token push in a try/catch (or push-then-pull pattern) so that a reverting transfer to a blacklisted beneficiary doesn't block delivery indefinitely — e.g. credit an internal claimable balance the beneficiary (or an alternate address they control) can withdraw later, instead of requiring `safeTransfer` to succeed to a fixed address.
- Alternatively, allow the mint/beneficiary address used in `onAccept` to be redirected/claimed by the original sender via a follow-up recovery mechanism when the primary transfer permanently fails.

### Proof of Concept
1. Alice holds the underlying ERC20 (USDC) on chain A and calls `WrappedHyperFungibleToken.send({dest: chainB, to: Bob, amount: X, timeout: 0, relayerFee: r, data: ""})`. Her USDC is locked in the `WrappedHyperFungibleToken` contract via `safeTransferFrom` [8](#0-7) ; `timeoutTimestamp` is set to `0` per `EvmHost.dispatch(DispatchPost)` [9](#0-8) .
2. Bob is already blacklisted by USDC on chain B (or becomes blacklisted before delivery).
3. A relayer submits the proof; `EvmHost.dispatchIncoming(PostRequest,...)` calls `onAccept`, which attempts `IERC20(_underlying).safeTransfer(Bob, X)` and reverts [1](#0-0) .
4. Because `!success`, the host only deletes `_requestReceipts[commitment]` to allow a retry [10](#0-9)  — but every future retry fails identically, forever.
5. Because `timeoutTimestamp == 0`, `Message.timeout()` returns `type(uint64).max` [5](#0-4) , so the request can never be proven "timed out," and `onPostRequestTimeout` (the only refund path) can never be invoked.
6. Alice's locked USDC on chain A is permanently frozen with no delivery and no refund path.

### Citations

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-360)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
```

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

**File:** evm/src/core/EvmHost.sol (L921-944)
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-326)
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L327-360)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleTokenUpgradeable.Message memory message =
            abi.decode(request.body, (HyperFungibleTokenUpgradeable.Message));
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

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
    }
```
