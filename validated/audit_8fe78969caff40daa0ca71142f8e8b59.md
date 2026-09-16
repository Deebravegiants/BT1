Confirms the same vulnerable pattern in the upgradeable variant.

### Title
`WrappedHyperFungibleToken.send()` uses requested amount instead of actual received amount for fee-on-transfer underlying tokens, causing under-collateralized cross-chain unlocks - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` (and its upgradeable twin `WrappedHyperFungibleTokenUpgradeable`) is a lock-and-mint/unlock token bridge: `send()` locks the caller's underlying ERC20 on the source chain and dispatches an ISMP message whose body encodes the *requested* `params.amount`; `onAccept()` on the destination chain unconditionally unlocks (`safeTransfer`s) that same `message.amount` of underlying token to the beneficiary. If the underlying token charges a transfer fee (fee-on-transfer / deflationary ERC20), the amount actually locked in the contract is less than `params.amount`, but the message dispatched — and thus the amount unlocked on the destination — still equals the full, unreduced `params.amount`.

### Finding Description
In `send()`, the underlying token is pulled via `safeTransferFrom` and `params.amount` is used both for the transfer and for building the cross-chain `Message.amount` field, with no balance-before/after check: [1](#0-0) 

The message body is built directly from `params.amount` in `_buildDispatchPost`, not from any measured "actually received" value: [2](#0-1) 

On the receiving chain, `onAccept()` unlocks exactly `message.amount` of the underlying token to the beneficiary, and `onPostRequestTimeout()` similarly re-mints/unlocks `message.amount` back to the sender on timeout: [3](#0-2) [4](#0-3) 

This is the exact bug class described in the external report: an amount taken as an input parameter is used for both accounting/minting and the `safeTransferFrom` call, without reconciling it against the actual balance delta caused by a fee-on-transfer token. Notably, the sibling contract `IntentGatewayV2.placeOrder()` in the same codebase explicitly guards against this by measuring `balanceOf` before/after the transfer and mutating `order.inputs[i].amount` to the actual received amount before computing escrow and commitments: [5](#0-4) 
`WrappedHyperFungibleToken.send()` has no equivalent guard, showing the safe pattern exists elsewhere in the codebase but was not applied here.

The upgradeable variant has the identical unguarded pattern: [6](#0-5) 

### Impact Explanation
Each `send()` call with a fee-on-transfer underlying token locks `params.amount − fee` in the contract but instructs the destination chain to unlock the full `params.amount`. Over repeated calls this produces a growing solvency gap in the underlying-token reserves held by the wrapper on the receiving side, which is drained faster than it was funded. Eventually legitimate later unlocks/redemptions will fail or exhaust the reserve entirely, meaning other users' locked funds become unrecoverable — a permanent freezing/loss-of-funds condition affecting the whole pool, not just the sender of the underpriced message. This is reachable by any unprivileged user who calls `send()` with an eligible fee-on-transfer underlying token configured via `configure()`.

### Likelihood Explanation
Likelihood depends on the owner configuring a fee-on-transfer ERC20 as `_underlying` via `configure()`. Given `configure()` places no restriction preventing deflationary/fee tokens (unlike an allowlist of vetted standard tokens), and the docs/README frame this as a general-purpose "cross-chain wrapper for existing ERC20 tokens," any current or future deployment for a token with transfer tax or rebasing/burn-on-transfer mechanics is directly exploitable by ordinary users through the normal `send()` entrypoint — no privileged access required.

### Recommendation
Measure the actual amount received by the contract (balance before/after `safeTransferFrom`, mirroring the pattern already used in `IntentGatewayV2.placeOrder()`) and use that measured amount — not `params.amount` — both when encoding the dispatched `Message.amount` and in the emitted `Sent` event, so that the amount promised for unlocking on the destination chain never exceeds what was actually locked on the source chain.

### Proof of Concept
1. Owner (or any deployer) configures `WrappedHyperFungibleToken` with `_underlying` set to a token that deducts, e.g., a 1% fee on `transferFrom` (fee burned or sent elsewhere).
2. User calls `send({amount: 1000e18, to: recipient, dest: chainB, ...})`. The contract's `safeTransferFrom` actually credits only 990e18 to the wrapper, but `_buildDispatchPost` encodes `amount: 1000e18` in the dispatched message.
3. On chain B, `onAccept()` decodes `message.amount = 1000e18` and unlocks 1000e18 of the underlying token to `recipient` — 10e18 more than was ever locked on chain A.
4. Repeating this process systematically drains chain B's underlying token reserve relative to chain A's actual locked balance, eventually causing other users' unlock/timeout-refund calls to fail due to insufficient reserve (permanent loss of funds for the pool).

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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
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
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L256-301)
```text
    function _buildDispatchPost(HyperFungibleTokenUpgradeable.SendParams calldata params)
        internal
        view
        returns (DispatchPost memory)
    {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(
            HyperFungibleTokenUpgradeable.Message({
                from: abi.encodePacked(msg.sender),
                to: params.to,
                amount: params.amount,
                data: params.data
            })
        );

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }

    /**
     * @notice Locks underlying tokens and dispatches a cross-chain transfer message
     * @dev If `_isWeth` is true and msg.value is sufficient, wraps native tokens via the underlying's WETH
     * deposit function (reverts if the underlying is not WETH). The remainder of msg.value
     * after wrapping is forwarded as native payment for dispatch fees.
     *
     * If `_isWeth` is false, locks ERC20 tokens via safeTransferFrom and pays
     * dispatch fees in the host's fee token (pulled from msg.sender).
     *
     * @param params The send parameters including destination, recipient, amount, and optional calldata
     */
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }
```
