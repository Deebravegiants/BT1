Confirmed: `WrappedHyperFungibleToken.send()` at [1](#0-0)  unconditionally trusts `params.amount` as the amount locked, without measuring the actual balance delta from `safeTransferFrom`. This is the exact analog of the Mellow stETH bug class, applicable here to `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`, which is reachable by any unprivileged token bridger via a single `send()` transaction.

### Title
Wrapped HFT trusts requested amount instead of actual tokens received on lock, causing under-collateralized cross-chain mint and refund DoS - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then encodes `params.amount` verbatim into the cross-chain `Message` dispatched to the peer contract, without verifying that the contract's balance actually increased by `params.amount`. For any underlying token whose transfer semantics deliver less than the requested amount (rebasing/share-based tokens such as stETH, or fee-on-transfer tokens), the wrapper will have locked less than it reports, while the remote `HyperFungibleToken` mints the full reported amount and the local timeout/refund path promises to pay back the full reported amount.

### Finding Description
In `send()`: [1](#0-0) 
the contract does `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` and immediately builds the dispatch message with `amount: params.amount` (see `_buildDispatchPost`, [2](#0-1) ). There is no balance-before/balance-after check, unlike the pattern already used elsewhere in the codebase in `IntentGatewayV2.placeOrder` ( [3](#0-2) ), which explicitly measures `IERC20(token).balanceOf(address(this))` before and after the transfer to compute the "actual received" amount for tokens with transfer-time deductions.

Because `WrappedHyperFungibleToken` skips this check:
1. If the underlying token delivers `params.amount - δ` (δ from rounding, e.g. stETH's documented 1-2 wei corner case, or a fee-on-transfer token), the wrapper's true escrowed balance is short by δ, but the dispatched `Message.amount` still equals the full requested `params.amount`.
2. The peer `HyperFungibleToken` on the destination chain mints `message.amount` in full on `onAccept` (`HyperFungibleToken` mint path referenced in `BridgeToken`/`HyperFungibleToken` docs), so the minted synthetic supply on remote chains becomes larger than the actual underlying locked on the home chain — an unbacked-mint style discrepancy that compounds with every `send()` call using a lossy-transfer token.
3. If the message instead times out, `onPostRequestTimeout` calls `IERC20(_underlying).safeTransfer(refundee, message.amount)` using the full recorded amount ( [4](#0-3) ). Once the wrapper's real balance is less than the sum of amounts it believes it holds, this `safeTransfer` reverts, denying the refund to that user and — because balances are shared across all users of the wrapper — potentially blocking any subsequent redemption/timeout/`onAccept` calls that need more balance than the contract actually possesses.

The identical unchecked pattern exists in `WrappedHyperFungibleTokenUpgradeable.send()` ( [5](#0-4) ) and its `onPostRequestTimeout`.

### Impact Explanation
This breaks the fundamental invariant documented for the HFT architecture: "the supply of this token is always backed by the pallet's escrow account" / wrapper's locked balance (see `BridgeToken.sol` doc comment, [6](#0-5) ). A lossy-transfer underlying causes the minted representation on remote chains to permanently exceed the actual locked collateral on the home chain, and causes legitimate refunds/unlocks to revert once the shortfall accumulates enough to exceed the contract's real balance — a denial of service for users trying to reclaim locked funds, and a systemic under-collateralization (some users' locked tokens become permanently unredeemable) for the wrapped asset. This is reachable by any unprivileged user calling `send()`; no privileged role is required to trigger it, only that the configured `underlying` token exhibits transfer-amount rounding or fee-on-transfer behavior.

### Likelihood Explanation
Likelihood depends on the owner configuring `WrappedHyperFungibleToken` with an underlying token that has non-1:1 transfer semantics (rebasing tokens like stETH, or fee-on-transfer tokens). Given stETH-class tokens are common bridging targets and the report class explicitly cites this behavior as a known, publicly documented corner case, and given the codebase's own `IntentGatewayV2` tests explicitly cover fee-on-transfer scenarios (proving the team is aware of and mitigates this pattern elsewhere), the omission of the same guard in `WrappedHyperFungibleToken` is a realistic configuration-dependent but easily triggered issue for any deployment using such an underlying.

### Recommendation
In `send()`, measure `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual received delta as `message.amount` (and as the amount used for fee/other accounting), mirroring the pattern already implemented in `IntentGatewayV2.placeOrder` ( [7](#0-6) ). Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.send()`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `underlying = stETH` (or any fee-on-transfer/rebasing ERC20).
2. User A calls `send({amount: 1000e18, dest: ..., ...})`. `safeTransferFrom` delivers `1000e18 - 2 wei` to the wrapper, but `Message.amount = 1000e18` is dispatched; on the destination chain the peer `HyperFungibleToken` mints `1000e18`.
3. Repeat across many `send()` calls; the wrapper's real stETH balance falls increasingly short of the sum of `message.amount` values it has promised across in-flight and refundable messages.
4. A subsequent message times out and `onPostRequestTimeout` attempts `safeTransfer(refundee, message.amount)` for the full recorded amount, but the wrapper's actual stETH balance is insufficient — the call reverts, permanently denying that user (and any other user whose refund/unlock draws on the same shared balance) their funds.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L234-253)
```text
    function _buildDispatchPost(HyperFungibleToken.SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(HyperFungibleToken.Message({
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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L313-323)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-318)
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
```

**File:** evm/src/apps/BridgeToken.sol (L26-29)
```text
 * @dev BRIDGE is native to nexus, so the two ends run the escrow model: `pallet-hyper-fungible-token`
 * escrows the native balance on nexus and this contract mints the equivalent here, meaning the supply
 * of this token is always backed by the pallet's escrow account. Sending back burns here and releases
 * there.
```
