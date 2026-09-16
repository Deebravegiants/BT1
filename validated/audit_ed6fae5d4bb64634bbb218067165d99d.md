## Analog Confirmed

### Title
Fee-on-transfer/deflationary `underlying` tokens break accounting in `WrappedHyperFungibleToken.send()` / `WrappedHyperFungibleTokenUpgradeable.send()`, allowing bridge reserve drain and unbacked unlocks - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` and its upgradeable counterpart lock the `_underlying` ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then encode the caller-supplied `params.amount` — not the amount actually received — into the cross-chain `Message` that is dispatched to the destination chain's peer contract. If `_underlying` is a fee-on-transfer/deflationary token, the contract receives strictly less than `params.amount`, but the destination chain still unlocks/mints the full `params.amount` when the message is delivered via `onAccept`.

### Finding Description
In `send()`: [1](#0-0) 

the token amount actually locked in the contract (post-fee) is never measured — no balance-before/balance-after check is performed, unlike the equivalent flow already hardened in `IntentGatewayV2.placeOrder()`: [2](#0-1) 

Instead, `_buildDispatchPost()` embeds the *requested* `params.amount` into the message body: [3](#0-2) 

On the destination chain (or on this same chain for lock/unlock pairs), `onAccept` unconditionally releases `message.amount` of the underlying/wrapped supply to the beneficiary: [4](#0-3) 

Because the amount released on delivery is always `>=` the amount actually escrowed on the sending chain, each transfer of a fee-on-transfer underlying token creates a permanent shortfall between the contract's real token balance and its cumulative outstanding liability to future `onAccept`/timeout-refund calls. The identical bug (and identical fix pattern) exists in `WrappedHyperFungibleTokenUpgradeable.send()`: [5](#0-4) 

This is precisely the bug class from the external report: `token.safeTransferFrom(msg.sender, address(this), _amount)` is trusted to have moved the full `_amount`, and that unchecked `_amount` is then propagated into downstream accounting (here, the cross-chain settlement amount) instead of being reconciled against the actual balance delta.

### Impact Explanation
Every `send()` call with a deflationary/fee-on-transfer `_underlying` token under-collateralizes the contract relative to what it commits to release on `onAccept`/timeout refund. Since `WrappedHyperFungibleToken` is a shared-custody pool (not per-order escrow like `IntentGatewayV2`), this shortfall accumulates across all users of that token pair: eventually the contract's real balance of `_underlying` is insufficient to honor legitimate unlocks/refunds for other users, i.e. permanent freezing/loss of funds for later senders and, in a lock/unlock bidirectional pairing, an unbacked mint/unlock of the wrapped asset on the peer chain relative to what was actually escrowed.

### Likelihood Explanation
Any unprivileged user can trigger this simply by calling `send()` when the configured `_underlying` is a fee-on-transfer token (a legitimate, common ERC20 design, not attacker-controlled malicious admin behavior) — no special privileges are required, and the owner's normal act of configuring such a token via `configure()` is not itself malicious.

### Recommendation
Measure the actual amount received by comparing `_underlying` balance before and after the `safeTransferFrom` call (as already done in `IntentGatewayV2.placeOrder()`), and use that measured amount both for the locked-balance accounting and for the `amount` field encoded into the dispatched `Message`, rather than trusting the caller-supplied `params.amount`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` = a 1% fee-on-transfer token.
2. Alice calls `send({amount: 1000e18, ...})`. `safeTransferFrom` moves 1000e18 requested but the contract only receives 990e18 due to the transfer fee.
3. `_buildDispatchPost` still encodes `amount: 1000e18` in the `Message`, and the ISMP request is dispatched with that full amount.
4. On the destination chain (or via same-chain timeout refund on this chain), `onAccept`/`onPostRequestTimeout` unlocks/mints/transfers `1000e18` — 10e18 more than was ever actually escrowed.
5. Repeating this drains the contract's real underlying-token reserve below its committed liabilities, causing later legitimate unlocks/refunds to fail or be paid out of other users' deposited principal.

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
