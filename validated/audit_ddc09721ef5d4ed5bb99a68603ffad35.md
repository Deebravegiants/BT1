Confirmed: `WrappedHyperFungibleToken.send()` locks `params.amount` via `safeTransferFrom` without measuring actual received balance, unlike `IntentGatewayV2.placeOrder()` which explicitly reconciles for fee-on-transfer tokens by measuring balance before/after. This is a solid analog to the deprecated-cToken bug class (unsupported token class breaks core accounting/solvency).

### Title
WrappedHyperFungibleToken does not support fee-on-transfer/deflationary ERC20 underlyings, causing unbacked cross-chain mints and reserve insolvency - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` assumes the underlying ERC20 always transfers the exact `params.amount` requested. For deflationary/fee-on-transfer or rebasing-down tokens, the contract actually receives less than `params.amount`, yet it dispatches a cross-chain message promising the full `params.amount`, which the destination chain's `HyperFungibleToken` mints or the counterpart `WrappedHyperFungibleToken` unlocks in full.

### Finding Description
In `send()`, the underlying token is pulled via `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` with no balance-before/balance-after check [1](#0-0) . The `Message.amount` field embedded in the dispatched `DispatchPost` is `params.amount` — the requested amount, not the actual amount received by the contract [2](#0-1) . On the receiving side, `onAccept` unconditionally transfers out `message.amount` of the underlying (or the `HyperFungibleToken` on a remote chain mints `message.amount` of the wrapped representation) [3](#0-2) . There is no reconciliation logic analogous to the fee-on-transfer handling implemented elsewhere in this same codebase for `IntentGatewayV2.placeOrder()`, which explicitly measures `balanceOf` before and after each transfer and mutates the order amount to the actually-received value before computing commitments/escrow [4](#0-3) . The identical unguarded pattern also exists in `WrappedHyperFungibleTokenUpgradeable.send()` [5](#0-4) .

### Impact Explanation
Each time a user bridges a fee-on-transfer or deflationary token through `WrappedHyperFungibleToken`, the contract's underlying reserve accumulates a permanent shortfall equal to the transfer fee, while the destination side mints/unlocks the full requested amount. Over repeated transfers this creates an unbacked liability: the wrapper's underlying balance can no longer cover all outstanding bridged supply, so the last users attempting to bridge back (unlock) will find the contract insolvent and their transfer will revert or drain reserves meant for other users — a permanent freezing/loss of funds for legitimate token holders. This matches the "unbacked mint" / "permanent freezing of funds" class of impact.

### Likelihood Explanation
Any owner can call `configure()` to set `_underlying` to any ERC20, and many real-world tokens implement transfer fees, rebasing, or other deflationary mechanics (e.g., certain stablecoins with configurable fees, reflection tokens). No validation prevents such tokens from being configured as the underlying, and a single ordinary `send()` call by any unprivileged user is sufficient to trigger the shortfall — no special privileges or governance action are required to reach this path.

### Recommendation
Mirror the fee-on-transfer handling already implemented in `IntentGatewayV2.placeOrder()`: measure `IERC20(_underlying).balanceOf(address(this))` before and after the `safeTransferFrom` call in `send()` (and the WETH-deposit branch, if the WETH implementation can also be non-standard), and use the actual received delta as `Message.amount` in the dispatched request rather than the caller-supplied `params.amount`. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.send()`.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` set to a deflationary ERC20 that charges a 1% fee on every transfer.
2. Alice calls `send({amount: 1000e18, ...})`. `safeTransferFrom` pulls 1000e18 from Alice but the contract's balance only increases by 990e18 (1% fee burned/redirected).
3. `_buildDispatchPost` still encodes `Message.amount = 1000e18` and dispatches the POST request.
4. On the destination chain, `HyperFungibleToken.onAccept` mints Bob 1000e18 of the wrapped representation — 10e18 more than what is actually held in reserve on the source chain.
5. Repeating this pattern accumulates an unbacked deficit; eventually a legitimate unlock/burn-back request on the source chain reverts due to insufficient underlying balance, permanently freezing funds for the affected user(s).

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-301)
```text
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }
```
