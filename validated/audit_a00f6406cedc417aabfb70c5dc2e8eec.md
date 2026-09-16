## Finding: Zero-Amount Cross-Chain Transfer Permanently Stalls Message Delivery for Weird-ERC20 Underlying Tokens

### Title
Bridging a `WrappedHyperFungibleToken` transfer with `amount = 0` permanently stalls ISMP message delivery for underlying tokens that revert on zero-value transfers - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol` / `WrappedHyperFungibleTokenUpgradeable.sol`)

### Summary
`HyperFungibleToken.send()` and `WrappedHyperFungibleToken.send()` do not validate that `params.amount > 0`. A caller can dispatch a cross-chain transfer with `amount = 0`. On the destination side, `WrappedHyperFungibleToken.onAccept()` unconditionally calls `IERC20(_underlying).safeTransfer(beneficiary, message.amount)`. If the wrapped underlying token reverts on zero-value transfers (a known "weird ERC20" behavior, e.g. LEND-style tokens), this call reverts, and the ISMP POST request can never be successfully delivered.

### Finding Description
`send()` in `sdk/packages/core/contracts/apps/HyperFungibleToken.sol` performs no amount check: [1](#0-0) 

`WrappedHyperFungibleToken.send()` similarly locks the underlying token via `safeTransferFrom` with no amount check, and the same struct/flow is shared for dispatch: [2](#0-1) 

On the destination chain, `onAccept()` decodes the message and unconditionally transfers `message.amount` of the underlying token to the beneficiary, with no zero-amount guard: [3](#0-2) 

The identical unguarded pattern exists in the upgradeable variant: [4](#0-3) 

Because the SDK's `SendParams.timeout` field explicitly supports `0` for "no timeout, messages will never expire" (per the dispatch documentation), a caller can craft a zero-amount, zero-timeout transfer. If the underlying wrapped token is a "revert-on-zero-transfer" ERC20, the `onAccept` delivery call will revert every time it is attempted (by any relayer, indefinitely), and because timeout is disabled, the message can never be timed out and refunded either. This is a variant of the same bug class as the referenced Gitcoin `MerklePayoutStrategyImplementation` report: an ERC20 transfer of `message.amount` is performed without checking for a non-zero value, and some real-world tokens revert on zero-value transfers.

### Impact Explanation
This causes a permanently undeliverable message on a legitimate Hyperbridge token-bridging route: relayers can never successfully submit the proof for this POST request because `onAccept` will always revert, and with `timeout = 0` the request can never be cancelled/refunded on the source chain either. This matches the "route unable to deliver messages" / permanent freeze criteria — any relayer fee escrowed for the request is also stuck since the delivery/timeout path (which pays out the relayer fee) never completes.

### Likelihood Explanation
Likelihood depends on deployment of a `WrappedHyperFungibleToken` around an underlying ERC20 that reverts on zero-value transfers. This is a known, documented category of ERC20 behavior (weird-erc20 "revert-on-zero-value-transfers"), and the wrapped-token app is explicitly designed to support arbitrary underlying ERC20s. Any user (not just an attacker) can trigger this unintentionally by simply sending `amount = 0`, or an attacker can deliberately do it with `timeout = 0` to permanently DoS the bridging route for that token pair.

### Recommendation
Add an explicit `amount > 0` check in `send()` for both `HyperFungibleToken` and `WrappedHyperFungibleToken` (and their upgradeable variants), reverting with a clear error (e.g. `ZeroAmount()`) before burning/locking and dispatching. Alternatively/additionally, guard the transfer calls in `onAccept`/`onPostRequestTimeout` to skip `safeTransfer`/`safeTransferFrom` when `amount == 0`.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` wrapping an ERC20 that reverts on zero-value `transfer` (per `https://github.com/d-xo/weird-erc20/blob/main/src/RevertZero.sol`).
2. Call `send()` with `SendParams{ amount: 0, timeout: 0, ... }`. This succeeds on the source chain (locks 0 tokens, dispatches POST request). [5](#0-4) 
3. When a relayer submits the proof to the destination `EvmHost`/`HandlerV2`, `onAccept()` is invoked and calls `IERC20(_underlying).safeTransfer(beneficiary, 0)`, which reverts against the weird-ERC20 underlying. [6](#0-5) 
4. Because `timeout = 0` ("no timeout... messages will never expire" per SDK docs), the request can never expire or be refunded, leaving it permanently undeliverable.

Note: I was unable to fully confirm within the available context whether `onAccept` is invoked from `EvmHost`/`HandlerV2` via a low-level `.call()` (allowing indefinite relayer retries against the same commitment, as seen in `EvmHost.dispatchTimeOut`) or via a direct interface call that would abort the whole batched handler transaction; either way the specific message's `onAccept` delivery can never succeed, so the request remains permanently stuck. [7](#0-6)

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-270)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-290)
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L327-353)
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
```

**File:** evm/src/core/EvmHost.sol (L856-877)
```text
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```
