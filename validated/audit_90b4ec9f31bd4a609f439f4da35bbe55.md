### Title
Permanent freezing of locked funds in `WrappedHyperFungibleToken` when the underlying token blacklists a beneficiary or refund recipient - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` locks an arbitrary underlying ERC20 (explicitly intended to support tokens like USDC) and unlocks/refunds it via plain `safeTransfer` calls in `onAccept` and `onPostRequestTimeout`, with no fallback path if the transfer reverts and no admin rescue function. A blacklistable underlying token (e.g. USDC) can permanently trap the escrowed funds for a given cross-chain transfer if either the destination beneficiary or the original sender (refund recipient) is later blacklisted by the token issuer.

### Finding Description
`send()` locks the underlying ERC20 via `safeTransferFrom` into the contract [1](#0-0) . On delivery, `onAccept` unconditionally calls `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` to push funds to the destination address supplied by the original sender [2](#0-1) . If delivery fails (for any reason, including this one), `EvmHost.dispatchIncoming` catches the low-level call failure, deletes the request receipt, and returns without reverting, explicitly "so that it can be retried" [3](#0-2) . If `beneficiary` is on the USDC blacklist, every retry of `onAccept` will hit the exact same `safeTransfer` call with the exact same blacklisted address and revert identically forever — the message can never be delivered.

The only other exit for locked funds is `onPostRequestTimeout`, which — once the request has timed out on the source chain — refunds `message.from` (the original sender) via the same unconditional `safeTransfer` pattern [4](#0-3) . If the original sender's address is itself blacklisted (e.g. their wallet was compromised and later blacklisted, a documented real-world USDC scenario), this refund path also reverts unconditionally and can never succeed.

Neither `onAccept` nor `onPostRequestTimeout` wraps the token transfer in a try/catch to skip/escrow the stuck transfer, and the contract exposes no owner/rescue function to sweep tokens out to an alternate address — `configure`, `addChain`, `removeChain`, `pause`/`unpause` are the only privileged functions available [5](#0-4) . Once both the delivery path and the timeout-refund path are blocked by blacklisting, the locked underlying tokens for that transfer are permanently stuck in the contract with no code path to recover them. `WrappedHyperFungibleTokenUpgradeable` contains the identical unconditional-transfer pattern in both `onAccept` and `onPostRequestTimeout` [6](#0-5) .

### Impact Explanation
This is a token-bridge lock/unlock path reachable by any ordinary user via `send()` and any unprivileged relayer submitting the resulting proof — no protocol-privileged actor is required; the only external trigger is the token issuer's independent blacklist decision, which is a documented and unprivileged-from-Hyperbridge's-perspective external event (per the original report, 200+ USDC addresses are already blacklisted for unrelated reasons). Once both the beneficiary and the refund/sender address involved in a specific transfer are unable to receive the underlying token, the locked funds for that transfer are permanently frozen in the `WrappedHyperFungibleToken` contract with no recovery mechanism, matching the "permanent freezing of funds" criterion.

### Likelihood Explanation
Requires the underlying wrapped token to support address-level blocklisting (explicitly the design's stated use case — wrapping arbitrary ERC20s such as USDC) and requires either the destination beneficiary or the original sender to become blacklisted before/while a bridge transfer is in flight. Given USDC's active and growing blacklist and the deprecated shared-custody pool this app family was designed to replace by isolating per-token risk, this is a realistic condition for any bridge deployment using a blacklistable underlying token, though it depends on that external blacklisting event rather than an attacker-controlled trigger alone.

### Recommendation
Wrap the `safeTransfer` calls in `onAccept` and `onPostRequestTimeout` in a try/catch (or use a pull-based claim/escrow pattern) so a reverting transfer to a blacklisted address does not permanently block that specific transfer's funds; on failure, credit the amount to an internal claimable balance (redeemable to an alternate address) instead of leaving it unrecoverable, and/or add an owner-gated emergency rescue function scoped to funds that have been undeliverable for an extended period.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` with `_underlying` = USDC, `_isWeth` = false.
2. User A calls `send()` with `params.to` = address `X` (not yet blacklisted), locking USDC into the contract [1](#0-0) .
3. Before the message is relayed and delivered, Circle blacklists address `X` (or `X` was already compromised/blacklisted).
4. A relayer submits `HandlerV2.handlePostRequests`, which calls `EvmHost.dispatchIncoming` → `onAccept` → `safeTransfer(X, amount)`, which reverts because `X` is blacklisted; the host swallows the revert and deletes the receipt "so it can be retried" [3](#0-2) . Every subsequent retry fails identically.
5. Once the request times out, someone submits `handlePostRequestTimeouts`, which calls `onPostRequestTimeout` to refund User A (`message.from`) [4](#0-3) . If User A's own address is also blacklisted (e.g. the same compromise event that led to the funds being sent), this refund also reverts unconditionally, and the locked USDC is now permanently stuck in the contract with no rescue function available.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L178-220)
```text
    function configure(WrappedConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
        _underlying = options.underlying;
        _isWeth = options.isWeth;
    }

    /**
     * @notice Registers a supported chain and its corresponding wrapper contract address
     * @dev Only callable by the contract owner
     * @param chainId The chain identifier (e.g., StateMachine.evm(1))
     * @param moduleId The module ID of the peer on the specified chain
     */
    function addChain(bytes calldata chainId, bytes calldata moduleId) external onlyOwner {
        _supportedChains[chainId] = moduleId;
    }

    /**
     * @notice Removes a chain from the supported set
     * @dev Only callable by the contract owner. After removal, transfers to/from this chain will revert.
     * @param chainId The chain identifier to remove
     */
    function removeChain(bytes calldata chainId) external onlyOwner {
        delete _supportedChains[chainId];
    }

    /**
     * @notice Pauses all cross-chain operations (send and receive)
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-365)
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
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** evm/src/core/EvmHost.sol (L809-818)
```text
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L327-390)
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

    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Attempts to unwrap WETH and refund native tokens.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleTokenUpgradeable.Message memory message =
            abi.decode(incoming.request.body, (HyperFungibleTokenUpgradeable.Message));
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
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```
