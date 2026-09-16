### Title
Fee-on-transfer underlying tokens desynchronize lock/unlock accounting in `WrappedHyperFungibleToken` - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom` but never verifies the amount actually received by the contract. It always encodes and dispatches `params.amount` — the user-requested amount — into the cross-chain `Message`, rather than the balance actually transferred in. If the underlying token charges a transfer fee (or has any deflationary/rebasing behavior), the source-chain contract locks less than `params.amount` while the destination-chain peer unlocks the full `params.amount` to the beneficiary, permanently desynchronizing the two deployments' underlying-token accounting.

### Finding Description
`send()` performs the token pull like this: [1](#0-0) 

Note it does not measure balance-before/after around `safeTransferFrom`; it simply assumes the contract now holds `params.amount` of `_underlying` and encodes that exact figure into the message body built by `_buildDispatchPost`: [2](#0-1) 

On the destination chain, `onAccept` blindly unlocks `message.amount` of the underlying to the beneficiary from its own local liquidity pool of the same underlying token, with no cap tied to what was actually received on the source side: [3](#0-2) 

The same flaw exists in the timeout refund path, which re-pays `message.amount` (the originally requested amount, not the actually-locked amount) back to the sender: [4](#0-3) 

And identically in the upgradeable variant: [5](#0-4) [6](#0-5) 

This is the exact bug class from the external report: the amount actually moved by an external token transfer is not checked, and the nominal/requested amount is used for internal accounting instead — here, that internal accounting is the locked-vs-unlocked balance parity between two `WrappedHyperFungibleToken` deployments bridging the same underlying asset.

Critically, this codebase already demonstrates awareness of and a correct fix for this exact issue elsewhere: `IntentGatewayV2.placeOrder` explicitly snapshots balances before and after `safeTransferFrom` and rewrites `order.inputs[i].amount` to the actually-received amount for fee-on-transfer tokens: [7](#0-6) 

`WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` do not apply this same actual-received-amount pattern.

### Impact Explanation
Each `send()` call with a fee-charging underlying token locks `params.amount - fee` but authorizes the destination peer to release the full `params.amount`. Over repeated transfers, the destination-side liquidity pool of the underlying token is drained faster than the source-side pool accumulates, since every transfer over-pays the destination relative to what was actually escrowed on the source. This is a permanent, unbacked depletion of pooled underlying funds on destination chains — later legitimate senders/receivers on that route can fail to be paid out (insolvency of the underlying pool), i.e. permanent freezing/loss of bridged funds and broken 1:1 backing across the bridge. Any deployment configured with a fee-on-transfer, deflationary, or otherwise non-standard ERC20 as `_underlying` is affected; this is entirely reachable by any unprivileged user simply calling `send()`.

### Likelihood Explanation
Likelihood depends on whether operators configure `_underlying` to a fee-on-transfer/deflationary token, which is plausible given `configure()` allows arbitrary owner-selected ERC20s and no code path enforces standard, non-fee-charging tokens. No special privileges are needed by the attacker/user beyond calling the public `send()` function with such a token configured; each call silently accrues the discrepancy.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2.placeOrder`: snapshot `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom` in `send()`, and use the actual received delta (not `params.amount`) both for the locked amount and for the `amount` field encoded into the dispatched `Message`. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` set to a token that charges a 1% transfer fee.
2. User calls `send({ amount: 1000e18, ... })`. `safeTransferFrom` moves `1000e18` requested, but the contract only receives `990e18` due to the fee; `_buildDispatchPost` still encodes `amount: 1000e18` in the `Message`.
3. The ISMP request is delivered to the destination chain's `WrappedHyperFungibleToken`, whose `onAccept` executes `IERC20(_underlying).safeTransfer(beneficiary, 1000e18)` — releasing 1000e18 from its local underlying pool even though only 990e18 was ever locked on the source side.
4. Repeating this drains the destination pool by the cumulative fee amount across all transfers, eventually preventing later transfers/refunds from being honored due to insufficient underlying balance on the destination contract.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-336)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-328)
```text
        } else {
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

                unchecked {
                    ++i;
                }
            }
```
