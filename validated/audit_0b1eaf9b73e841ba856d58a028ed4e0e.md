## Title
Fee-on-transfer underlying token causes `WrappedHyperFungibleToken` to over-unlock/over-refund tokens, draining the locked reserve - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken.send()` locks the underlying ERC20 via `safeTransferFrom` but never measures the amount actually received by the contract before encoding the cross-chain message. If `_underlying` is a fee-on-transfer (or otherwise deflationary) token, the contract receives less than `params.amount`, yet the dispatched message still carries the full, pre-fee `params.amount`. Both the destination-chain `onAccept()` unlock and the source-chain `onPostRequestTimeout()` refund pay out `message.amount` (the full pre-fee amount) instead of the amount actually escrowed, permanently draining the shared underlying-token reserve to the detriment of other users' locked balances.

### Finding Description
In `send()`, tokens are pulled with a plain `safeTransferFrom` and no before/after balance check: [1](#0-0) 

The message body built in `_buildDispatchPost` embeds the caller-supplied `params.amount` verbatim, not the actual tokens received: [2](#0-1) 

On the receiving side, `onAccept()` unconditionally transfers out `message.amount` of the underlying token to the beneficiary: [3](#0-2) 

Likewise, `onPostRequestTimeout()` refunds `message.amount` on the source chain if the message times out: [4](#0-3) 

This is exactly the bug class from the reference report: a transfer-in is assumed to deliver the full nominal amount, but a fee-on-transfer token delivers less, while downstream accounting (here, the cross-chain message and refund/unlock) still uses the pre-fee amount. Note that the sibling `IntentGatewayV2` contracts in this same repo explicitly guard against this by snapshotting `balanceOf` before/after `safeTransferFrom` and mutating the escrowed/committed amount to the actually-received value: [5](#0-4) 
`WrappedHyperFungibleToken` has no equivalent adjustment, so any fee-on-transfer or rebasing-deflationary underlying breaks its accounting.

### Impact Explanation
Every `send()` call with a fee-on-transfer underlying locks `params.amount * (1 - fee)` but authorizes the release of the full `params.amount` on the destination (via `onAccept`) or on refund (via `onPostRequestTimeout`). Because the contract is a shared pool backing all wrapped transfers for that underlying token, each such call permanently drains `fee * params.amount` more from the pool's actual token balance than it received. Over repeated calls (or a single large one) this can exhaust the underlying reserve, leaving legitimate unlock/refund requests from other users unable to be fully paid — a form of insolvency/fund-freezing for the shared collateral, and a direct value transfer benefiting whoever triggers the deflationary transfer at the expense of the pool.

### Likelihood Explanation
This is trivially triggerable by any user who calls `send()` while `_underlying` is configured (by the owner) as a fee-on-transfer or deflationary token, or if such a token is later substituted/upgraded as `_underlying` via `configure()`. No special privileges beyond being a normal token sender are required — it matches the "unprivileged token bridger" reachability requirement. The likelihood is contingent on the owner selecting/whitelisting a fee-on-transfer underlying, which is a realistic deployment/configuration risk for cross-chain wrapper contracts supporting arbitrary ERC20s.

### Recommendation
In `send()`, snapshot `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, and use the actual delta as `message.amount` in the dispatched message (mirroring the pattern already used in `IntentGatewayV2.placeOrder`). Alternatively, explicitly disallow fee-on-transfer/rebasing tokens as `_underlying` via documentation and/or a runtime check (e.g., verifying `balanceOf` delta equals the requested amount, reverting otherwise) to preserve 1:1 backing between locked collateral and message-authorized withdrawals.

### Proof of Concept
1. Owner configures `WrappedHyperFungibleToken` with `_underlying` = a token that charges 1% fee on transfer.
2. Alice calls `send({to: bob, amount: 1000e18, dest: chainB, ...})`. `safeTransferFrom` pulls 1000e18 nominal but the contract only receives 990e18 (10e18 taken as fee).
3. The dispatched `HyperFungibleToken.Message` still encodes `amount: 1000e18`.
4. On chain B, `onAccept()` decodes `message.amount = 1000e18` and calls `IERC20(_underlying).safeTransfer(bob, 1000e18)` — releasing 10e18 more than was ever locked on chain A.
5. Repeating this (or using a higher-fee token) drains the shared underlying reserve, eventually causing legitimate unlocks for other users to fail (`safeTransfer` reverts) or an outright loss of protocol funds.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
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
