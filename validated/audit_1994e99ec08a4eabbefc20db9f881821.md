### Title
Permanent freezing of locked funds in `WrappedHyperFungibleToken` when the underlying ERC20 becomes paused or its holder is blacklisted - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` locks an arbitrary externally-controlled ERC20 (`_underlying`) on `send()` and only releases it via `onAccept` (deliver to beneficiary) or `onPostRequestTimeout` (refund to sender). Both release paths perform a direct `IERC20(_underlying).safeTransfer(...)` with no fallback, so if the underlying token can be paused, or the specific beneficiary/refundee address can be blacklisted by the token issuer (e.g. USDC-style tokens), neither delivery nor timeout-refund can ever complete for the affected transfer, permanently locking the escrowed tokens in the contract with no rescue mechanism.

### Finding Description
`send()` escrows the underlying ERC20 via `safeTransferFrom` [1](#0-0) . When the ISMP message is delivered, `onAccept` pushes the underlying token straight to the beneficiary with `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` [2](#0-1) . The only two ways this escrowed value ever leaves the contract are this transfer, or the timeout refund `IERC20(_underlying).safeTransfer(refundee, message.amount)` in `onPostRequestTimeout` [3](#0-2) .

On the host side, `EvmHost.dispatchIncoming` invokes `onAccept` via a low-level `.call`; on failure it simply deletes the request receipt and returns so the request "can be retried" [4](#0-3) . This retry mechanism assumes failures are transient. It is not transient for a permanently blacklisted beneficiary or a permanently paused underlying token: every retry of `onAccept` will keep reverting until the request finally times out. At that point, `onPostRequestTimeout` attempts the refund — but if the underlying token is globally paused (issuer-level pause/emergency freeze) or the original sender (`refundee`) is itself blacklisted, `safeTransfer(refundee, ...)` in the timeout path reverts as well, per the same "callback must succeed before refund is possible" semantics described for the timeout handler (docs: "If callback reverts, no refund occurs. Timeout can be resubmitted until callback succeeds") [5](#0-4) .

There is no owner/admin rescue or sweep function in the contract to recover tokens stuck in this state — the only privileged calls are `configure`, `addChain`/`removeChain`, and `pause`/`unpause` [6](#0-5) , none of which can move locked underlying tokens out of the contract. Since both success paths (deliver, refund) depend unconditionally on a plain external ERC20 transfer succeeding, a paused-transfer or blacklisted-address condition on the underlying token makes the locked funds permanently unrecoverable. The same pattern also exists in `WrappedHyperFungibleTokenUpgradeable.sol` [7](#0-6) .

This is directly analogous to the reported issue class: the protocol does not account for tokens whose transfer functionality can be paused or made non-transferrable for specific addresses, resulting in funds that can neither be delivered nor withdrawn/refunded.

### Impact Explanation
Any user (unprivileged) who calls `send()` to bridge a `WrappedHyperFungibleToken`-wrapped ERC20 risks permanent loss of the escrowed principal if, before delivery or timeout-refund completes, the underlying token issuer pauses transfers or blacklists either the destination beneficiary or the original sender. The funds sit in the wrapper contract with no code path capable of moving them, meeting the "permanent freezing of funds" bar — this is not merely a delay, since the retry mechanism cannot succeed against a persistent, issuer-enforced restriction and there is no admin sweep function.

### Likelihood Explanation
Likelihood depends on the underlying token supporting pausability or address-level blocklisting (common for regulated/centralized stablecoins such as USDC/USDT), and on the wrapper being configured with such a token — a configuration decision made by the contract owner via `configure()`, not inherent to the bridge design, but a realistic and expected deployment scenario for a generic "wrap any ERC20" bridge app. Given `WrappedHyperFungibleToken` is explicitly designed to wrap arbitrary existing ERC20s, this condition is foreseeable rather than exotic.

### Recommendation
- Do not let a failing external token transfer permanently block the only redemption/refund path. Consider a pull-based claim pattern (credit an internal balance mapping for `beneficiary`/`refundee` on `onAccept`/`onPostRequestTimeout`, and let users call a separate `claim()` function to `safeTransfer` at their own risk/timing) so a transient or address-specific failure does not lock funds owed to other, unaffected recipients or block subsequent processing.
- Wrap the `safeTransfer` calls in `onAccept` and `onPostRequestTimeout` in a try/catch (or low-level call) so a reverting transfer records the amount as claimable/recoverable instead of reverting the whole callback.
- Provide an owner-gated emergency recovery mechanism (e.g., after a governance-approved delay) to redirect stuck balances if the underlying token becomes irrecoverably non-transferable for a specific address.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` = a pausable/blacklistable ERC20 (e.g., a USDC-like token) and adds a supported destination chain.
2. Alice calls `send()` with `amount = X`, locking `X` underlying tokens in the wrapper contract [1](#0-0) .
3. Before the message is delivered, the token issuer blacklists the destination `beneficiary` address (or pauses the token globally). Every relayer submission of `onAccept` now reverts at `safeTransfer(beneficiary, ...)`; `EvmHost.dispatchIncoming` swallows the revert and allows retry indefinitely, but retries never succeed [8](#0-7) .
4. Once the request times out, a relayer submits the timeout message, invoking `onPostRequestTimeout`, which attempts `safeTransfer(refundee, X)` to Alice. If instead the token issuer also paused the token globally (or Alice's own address is blacklisted, e.g. due to unrelated sanctions), this call reverts too [3](#0-2) .
5. `X` tokens are now permanently stuck in the `WrappedHyperFungibleToken` contract — no function exists to move them out.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L322-324)
```text
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

**File:** docs/content/developers/evm/api/ihandler.mdx (L140-149)
```text
1. Verifies timeout proof
2. For each request:
   - Validates timeout timestamp has passed
   - Calls `onPostRequestTimeout()` on source application
   - Refunds relayer fee to payer (only if callback succeeds)

**Important:**
- Application timeout callback is called **before** refund
- If callback reverts, no refund occurs
- Timeout can be resubmitted until callback succeeds
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
