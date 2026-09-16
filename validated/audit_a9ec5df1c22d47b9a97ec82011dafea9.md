### Title
Unchecked zero address recipient in `WrappedHyperFungibleToken.onAccept` (native-ETH path) permanently burns bridged funds - ([File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken.onAccept` (and its identical counterpart in `WrappedHyperFungibleTokenUpgradeable.onAccept`) extracts the destination-chain beneficiary from the cross-chain message body via `_toAddr(message.to)` without validating that the resulting address is non-zero. When the wrapper is configured as WETH (`_isWeth == true`), the delivery path performs a raw native-value push, `beneficiary.call{value: message.amount}("")`, which succeeds unconditionally when `beneficiary == address(0)` because a plain value transfer to an address with no code never reverts. This silently burns the unlocked ETH and marks the cross-chain request as successfully delivered, so no timeout/refund path is ever triggered.

### Finding Description
`onAccept` decodes the incoming `Message` and derives the recipient with: [1](#0-0) 
`_toAddr` only checks that the byte-length is 20, never that the value is non-zero: [2](#0-1) 

For WETH-mode wrappers, the delivery then unwraps WETH and attempts a direct native-ETH push to `beneficiary`: [3](#0-2) 

Unlike the non-WETH branch, which uses `IERC20(_underlying).safeTransfer(beneficiary, ...)` (OpenZeppelin ERC20 reverts on transfer to `address(0)`), a low-level `.call{value: ...}("")` to `address(0)` always succeeds because there is no contract code to execute at that address — the EVM simply credits the (unreachable) zero-address balance. Because `sent == true`, the fallback re-wrap-and-ERC20-transfer branch is never entered, so the ETH is unrecoverably lost. The `onAccept` call then completes successfully, so the ISMP host records the request as delivered — no timeout is ever raised and no refund mechanism (`onPostRequestTimeout`) is triggered.

The recipient (`message.to`) originates directly from `SendParams.to`, which is fully controlled by whoever calls `send()` on the source-chain deployment of `WrappedHyperFungibleToken`: [4](#0-3) 

This mirrors the reported `EthBridge.depositERC20To` issue exactly: an unchecked possibly-zero destination parameter that is reachable from an ordinary, unprivileged bridging transaction and leads to funds being locked/lost instead of reverting.

### Impact Explanation
When `_isWeth` is true, any message whose beneficiary resolves to `address(0)` causes the contract to unwrap WETH and send the underlying native ETH to the zero address, permanently destroying those funds with no recovery path (the request is marked delivered, so timeout-based refund logic in `onPostRequestTimeout` never runs). This is a permanent loss-of-funds bug in a live token-bridge delivery path, distinct from a simple griefing/self-mistake since it silently succeeds instead of failing safely like every other transfer path in the same contract.

### Likelihood Explanation
Reachable from a single, fully unprivileged transaction: any user calling `send()` on the peer `WrappedHyperFungibleToken` deployment with `to = abi.encodePacked(address(0))` (or any 20-byte zero value) triggers this on delivery, with no special permissions, governance, or malicious-relayer assumption required. The bug is deterministic and triggers on the very first delivery attempt.

### Recommendation
In `WrappedHyperFungibleToken.onAccept` and `WrappedHyperFungibleTokenUpgradeable.onAccept` (and analogously in `onPostRequestTimeout`), validate `beneficiary != address(0)` (and `refundee != address(0)`) immediately after `_toAddr` resolves the address, reverting the delivery if the check fails so the request is correctly retried/timed-out rather than silently succeeding and burning funds. Consider adding the same explicit zero-address guard used elsewhere in `_mint`-based flows to the raw `.call{value}` push path.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` on chain A and chain B, configured with `isWeth = true` and `_underlying` set to WETH; register each as the other's peer via `addChain`.
2. From chain A, any user calls `send()` with `SendParams.to = abi.encodePacked(address(0))` and `amount = X`, sending `msg.value >= X` so the contract wraps ETH into WETH and locks it (`WrappedHyperFungibleToken.sol:266-290`).
3. The ISMP relayer delivers the resulting POST request to chain B's `WrappedHyperFungibleToken.onAccept`.
4. In `onAccept`, `beneficiary = _toAddr(message.to) == address(0)`; the WETH is withdrawn to native ETH and `address(0).call{value: X}("")` executes and returns `sent == true` (no code to fail at address 0).
5. `onAccept` completes without reverting; the ISMP host records the request as delivered. The `X` ETH that was unwrapped is now held at `address(0)` — permanently unreachable — and no timeout/refund is ever generated for the original sender.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L238-253)
```text
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L306-307)
```text
        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-321)
```text
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L371-376)
```text
    function _toAddr(bytes memory b) internal pure returns (address addr) {
        if (b.length != 20) revert InvalidAddress(b.length);
        // casting to 'bytes20' is safe because we already checked length
        // forge-lint: disable-next-line(unsafe-typecast)
        return address(bytes20(b));
    }
```
