### Title
`WrappedHyperFungibleToken.send()` locks fee-on-transfer tokens without verifying actual received amount, causing cross-chain reserve insolvency - ([File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken.send()` calls `safeTransferFrom()` to lock the underlying ERC20 on the source chain but never checks how much was actually received. It then dispatches a cross-chain message declaring the caller-supplied `params.amount` verbatim, and the destination peer releases that full declared amount from its own reserve on `onAccept()`. If the underlying token charges a transfer fee (fee-on-transfer / deflationary token), the amount actually locked on the source chain is less than the amount unlocked on the destination chain, permanently draining the destination-side reserve pool relative to what was ever deposited.

### Finding Description
`send()` locks tokens like this: [1](#0-0) 

Unlike `_pullTokenInputAndPayProtocolFee()`'s `safeTransferFrom`, no balance-before/after check is performed. The dispatched message body embeds the caller's declared `params.amount`, not the actual amount received: [2](#0-1) 

On the destination chain, `onAccept()` unconditionally transfers out `message.amount` (the undiscounted, declared amount) from its own token reserve to the beneficiary: [3](#0-2) 

The codebase demonstrates that this exact hazard is known and has been explicitly mitigated elsewhere: `IntentGatewayV2.placeOrder()` snapshots the balance before and after `safeTransferFrom()` and uses the *actual received* amount for escrow/commitment, precisely to handle fee-on-transfer tokens: [4](#0-3) 

`WrappedHyperFungibleToken.send()` lacks this same defensive check, so it inherits the exact root cause from the external report: `safeTransferFrom()` succeeding is treated as proof that the full nominal amount was received, when in fact fee-on-transfer tokens deliver less.

### Impact Explanation
Each `send()` call on a fee-on-transfer underlying token locks `actual = amount - fee` on the source chain but the peer contract on the destination chain unlocks/releases the full undiscounted `amount` from its own reserve pool. Over repeated sends, the destination reserve is depleted faster than it is replenished by legitimate locks. This is a permanent, protocol-level insolvency: eventually a legitimate unlock will revert due to insufficient underlying balance on the destination side (`safeTransfer` in `onAccept` reverting), permanently freezing that user's bridged funds, while earlier callers effectively extract more value than they deposited. This is reachable by any unprivileged user who simply calls the public `send()` function with a fee-on-transfer token configured as `_underlying` — no special privileges required.

### Likelihood Explanation
Likelihood depends on the owner configuring a fee-on-transfer token as the wrapped `_underlying` asset via `configure()`. Fee-on-transfer/deflationary tokens are common in the wild (reflection tokens, some stablecoin variants with transfer taxes). Since `configure()`/`addChain()` are owner-controlled but the actual drain is triggerable by any user calling `send()`, once such a token is wrapped, exploitation (or accidental degradation) requires no special access — just ordinary use of the bridge, matching the exact scenario acknowledged in the referenced external report ("fee-on-transfer tokens are beyond the current scope... undefined behavior is an acceptable risk" was the response to the *analogous* Sudoswap issue, but here the consequence is loss of bridged funds rather than a pricing/fee bug).

### Recommendation
In `WrappedHyperFungibleToken.send()`, snapshot `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom()`, and use the actual delta (not `params.amount`) when building the dispatched `Message.amount`, mirroring the pattern already used in `IntentGatewayV2.placeOrder()`. Alternatively, explicitly disallow/flag fee-on-transfer tokens at `configure()` time, and document that only tokens with standard 1:1 transfer semantics may be wrapped.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` = a fee-on-transfer token charging 1% fee, and registers peer chains A and B.
2. User on chain A calls `send({amount: 1000e18, dest: B, to: recipient, ...})`. `safeTransferFrom` actually locks only 990e18 on chain A (1% burned/fee), but the dispatched `Message.amount` is 1000e18.
3. Relayer delivers the message to chain B; `onAccept()` calls `safeTransfer(recipient, 1000e18)`, releasing 1000e18 from chain B's reserve even though only 990e18 was ever backed by the corresponding lock.
4. Repeating this process (or a single large transfer) drains chain B's reserve pool beyond what legitimate locks have contributed, so a subsequent legitimate unlock reverts with insufficient balance — permanently freezing that user's funds.

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
